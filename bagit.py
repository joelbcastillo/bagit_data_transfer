import os
import sys
from datetime import date, datetime
import hashlib
import multiprocessing
import re
import wmi
import subprocess
import builtins

BAGIT_TXT = """BagIt-Version: 0.97\nTag-File-Character-Encoding: UTF-8\n"""
BAG_SOFTWARE_AGENT = 'BagIt Data Transfer v1.0 <http://github.com/joelbcastillo/bagit_data_transfer'
BLOCK_SIZE = 16384

ROBOCOPY_COMMAND = """robocopy {source} {destination} /W:0 /TEE /e /V /LOG:{log_file} /R:1 /ZB /COPYALL /np"""


def print(*args, **kwargs):
    return builtins.print("{}:\t".format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")), *args, **kwargs)


def make_bag(bag_dir, dst_path, bag_info=None, processes=1, checksum=['md5']):
    """
    Convert the bag_dir into a bag.
    :param bag_dir: Path to directory to be bagged
    :param bag_info: Dictionary of Bag-Info Metadata
    :param processes: Number of processes to be used to create the bag, defaults to 1
    :param checksum: Checksum algorithm to be used, defaults to MD5
    :param dest: Destination path for bag
    """
    bag_dir = os.path.abspath(bag_dir)
    global logfile
    logfile = os.path.join(dst_path, 'bagit_log-{}.txt'.format(datetime.strftime(datetime.now(), "%Y%m%d-%H%M%S")))
    logfile = open(logfile, 'a')

    print("Creating a bag for directory {}".format(bag_dir), file=logfile)

    if not os.path.isdir(bag_dir):
        print("Directory not found: {}".format(bag_dir), file=logfile)

    old_dir = os.path.abspath(os.getcwd())

    os.chdir(bag_dir)

    try:
        unbaggable = _can_bag(os.curdir)

        if unbaggable:
            print("Unable to write to the following directories: \n {}".format(unbaggable), file=logfile)
            exit(1)

        unreadable_dirs, unreadable_files = _can_read(os.curdir)

        if unreadable_dirs or unreadable_files:
            if unreadable_dirs:
                print("Unable to read the following directories: \n {}".format(unreadable_dirs), file=logfile)

            if unreadable_files:
                print("Unable to read the following files: \n {}".format(unreadable_files), file=logfile)

            exit(1)
        else:
            print("Creating data directory", file=logfile)

            cwd = os.getcwd()

            robocopy_command = ROBOCOPY_COMMAND
            logfile_name = "data_transfer_file_{date_time}.txt".format(
                date_time=datetime.strftime(datetime.now(), "%Y-%m-%d_%H:%M"))
            logfile_name = os.path.join(dst_path, logfile_name)
            robocopy_command = robocopy_command.format(source=bag_dir, destination=os.path.join(dst_path, 'data'),
                                                       log_file=logfile_name)

            robocopy_command = robocopy_command.split()

            if not os.path.exists(dst_path):
                os.mkdir(dst_path)

            logfile.write("{}:\t Running Robocopy\n".format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")))
            logfile.write("{}".format(robocopy_command))
            subprocess.call(robocopy_command, stdin=logfile, stdout=logfile, stderr=logfile)
            logfile.write(
                "{}:\t Done Running Robocopy\n".format(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")))

            # Set permisisons for payload directory
            os.chmod(dst_path, os.stat(cwd).st_mode)

            for c in checksum:
                print("Writing manifest-{}.txt".format(c), file=logfile)
                oxum = _make_manifest(os.path.join(dst_path, 'manifest-{}.txt'.format(c)), dst_path, processes, c)

            print("Writing bagit.txt", file=logfile)

            with open(os.path.join(dst_path, "bagit.txt"), "w+") as bagit_file:
                bagit_file.write(BAGIT_TXT)

            print("Writing bag-info.txt", file=logfile)

            if not bag_info:
                bag_info = {}

            # Set Bagging-Date
            bag_info['Bagging-Date'] = date.strftime(date.today(), "%Y-%m-%d")
            if "Bag-Software-Agent" not in bag_info:
                bag_info['Bag-Software-Agent'] = BAG_SOFTWARE_AGENT
            bag_info['Payload-Oxum'] = 0
            oxum = _make_tag_file(os.path.join(dst_path, 'bag-info.txt'), bag_info)

            for c in checksum:
                _make_tagmanifest_file(c, bag_dir, dst_dir=dst_path)

            # Get data for HDD
            drive_letter = bag_dir.split(':')[0]
            logical_disk, physical_disk = get_hdd_info(drive_letter)

            with open(os.path.join(dst_path, 'drive_info.txt'), 'w+') as drive_file:
                print("Creating drive information file", file=logfile)
                drive_file.write(str(logical_disk))
                drive_file.write(str(physical_disk))


    except Exception as e:
        print("An exception occurred creating the bag", file=logfile)
        print("{}".format(e), file=logfile)
        import traceback
        tb = sys.exc_info()
        traceback.print_exception(*tb)
        exit(1)

    finally:
        os.chdir(old_dir)
        return True


def get_hdd_info(drive_letter):
    print('printing hard drive info: {} '.format(drive_letter), file=logfile)

    c = wmi.WMI()

    # Dictionary of different MediaTypes
    media_type_dict = {"Removable media other than floppy": 11, "Fixed hard disk media": 12}

    # Dictionary of disk drive info
    disk_drive_info = {}

    # Dictionary of logical drive info
    logical_drive_info = {}

    for diskDrive in c.Win32_DiskDrive():
        for logicalDisk in c.Win32_LogicalDisk():
            if logicalDisk.name == drive_letter:
                if media_type_dict.get(diskDrive.mediaType, None) == logicalDisk.mediaType:
                    for key, value in diskDrive.properties.items():
                        disk_drive_info[key] = getattr(diskDrive, key)

                    for key, value in logicalDisk.properties.items():
                        logical_drive_info[key] = getattr(logicalDisk, key)

    return disk_drive_info, logical_drive_info


def _can_bag(test_dir):
    """
    Get list of unwriteable files/folders in test_dir
    :param test_dir:
    :return: Tuple of unwriteable files / folders
    """
    unwriteable = []

    for inode in os.listdir(test_dir):
        if not os.access(os.path.join(test_dir, inode), os.W_OK):
            unwriteable.append(os.path.join(os.path.abspath(test_dir), inode))

    return tuple(unwriteable)


def _can_read(test_dir):
    """
    Return ((unreadable_dirs), (unreadable_files))
    :param test_dir:
    :return: ((unreadable_dirs), (unreadable_files))
    """
    unreadable_dirs = []
    unreadable_files = []

    for dirpath, dirnames, filenames in os.walk(test_dir):
        for dn in dirnames:
            if not os.access(os.path.join(dirpath, dn), os.R_OK):
                unreadable_dirs.append(os.path.join(dirpath, dn))
        for fn in filenames:
            if not os.access(os.path.join(dirpath, fn), os.R_OK):
                unreadable_files.append(os.path.join(dirpath, fn))

    return tuple(unreadable_dirs), tuple(unreadable_files)


def _manifest_line(filename, algorithm='md5', block_size=BLOCK_SIZE):
    print("Generating checksum for file {}".format(filename), file=logfile)

    with open(filename, 'rb') as fh:
        m = _hasher(algorithm)

        total_bytes = 0

        while True:
            block = fh.read(block_size)
            total_bytes += len(block)
            if not block:
                break
            m.update(block)
    return m.hexdigest(), _decode_filename(filename), total_bytes


def _hasher(algorithm='md5'):
    if algorithm == 'md5':
        m = hashlib.md5()
    elif algorithm == 'sha1':
        m = hashlib.sha1()
    elif algorithm == 'sha256':
        m = hashlib.sha256()
    elif algorithm == 'sha512':
        m = hashlib.sha512()
    return m


def _encode_filename(s):
    s = s.replace("\r", "%0D")
    s = s.replace("\n", "%0A")
    return s


def _decode_filename(s):
    s = re.sub(r"%0D", "\r", s, re.IGNORECASE)
    s = re.sub(r"%0A", "\n", s, re.IGNORECASE)
    return s


def _manifest_line_md5(filename):
    return _manifest_line(filename, 'md5')


def _manifest_line_sha1(filename):
    return _manifest_line(filename, 'sha1')


def _manifest_line_sha256(filename):
    return _manifest_line(filename, 'sha256')


def _manifest_line_sha512(filename):
    return _manifest_line(filename, 'sha512')


def _make_manifest(manifest_file, data_dir, processes=1, algorithm='md5'):
    print("Writing manifest with {} processes".format(processes), file=logfile)

    try:
        manifest_line = {
            'md5': _manifest_line_md5,
            'sha1': _manifest_line_sha1,
            'sha256': _manifest_line_sha256,
            'sha512': _manifest_line_sha512,
        }[algorithm]
    except KeyError:
        print("Unknown algorithm: {}".format(algorithm), file=logfile)
        raise RuntimeError

    if processes > 1:
        pool = multiprocessing.Pool(processes=processes)
        checksums = pool.map(manifest_line, _walk(data_dir))
        pool.close()
        pool.join()
    else:
        checksums = [manifest_line(i) for i in _walk(data_dir)]

    with open(manifest_file, 'w+') as manifest:
        num_files = 0
        total_bytes = 0

        for digest, filename, byte_count in checksums:
            num_files += 1
            total_bytes += byte_count
            manifest.write("{} {} \n".format(digest, _encode_filename(filename)))

    return "{}.{}".format(total_bytes, num_files)


def _walk(data_dir):
    for dirpath, dirnames, filenames in os.walk(data_dir):
        # if we don't sort here the order of entries is non-deterministic
        # which makes it hard to test the fixity of tagmanifest-md5.txt
        filenames.sort()
        dirnames.sort()
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            # BagIt spec requires manifest to always use '/' as path separator
            if os.path.sep != '/':
                parts = path.split(os.path.sep)
                path = '/'.join(parts)
            yield path


def _make_tagmanifest_file(algorithm, bag_dir, dst_dir, block_size=BLOCK_SIZE):
    """

    :param algorithm:
    :param bag_dir:
    :return:
    """
    tagmanifest_file = os.path.join(dst_dir, "tagmanifest-%s.txt" % algorithm)
    print("Writing {}".format(tagmanifest_file), file=logfile)

    checksums = []

    for f in _find_tag_files(bag_dir):
        if re.match(r'^tagmanifest-.+\.txt$', f):
            continue
        with open(os.path.join(bag_dir, f), 'rb') as fh:
            m = _hasher(algorithm)
            while True:
                block = fh.read(block_size)
                if not block:
                    break
                m.update(block)
            checksums.append((m.hexdigest(), f))

        with open(os.path.join(dst_dir, tagmanifest_file), 'w') as tagmanifest:
            for digest, filename in checksums:
                tagmanifest.write('{} {}\n'.format(digest, filename))


def _find_tag_files(bag_dir):
    for fname in os.listdir(bag_dir):
        if fname == 'data' or fname.startswith('tagmanifest-'):
            continue
        absfname = os.path.join(bag_dir, fname)
        if os.path.isfile(absfname):
            yield (fname)
        elif os.path.isdir(absfname):
            for dir_name, _, filenames in os.walk(absfname):
                for f in filenames:
                    p = os.path.join(dir_name, f)
                    yield os.path.relpath(p, bag_dir)


def _make_tag_file(bag_info_path, bag_info):
    headers = sorted(bag_info.keys())

    with open(bag_info_path, 'w') as f:
        for h in headers:
            if isinstance(bag_info[h], list):
                for val in bag_info[h]:
                    f.write("{}: {}\n".format(h, val))
            else:
                txt = bag_info[h]
                # strip CR, LF and CRLF so they don't mess up the tag file
                txt = re.sub(r'\n|\r|(\r\n)', '', str(txt))
                f.write("{}: {}\n".format(h, txt))
