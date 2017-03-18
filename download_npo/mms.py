# encoding:utf-8
# pylint:disable=too-few-public-methods

import ctypes
import ctypes.util
import sys
import download_npo


class mms_stream_t(ctypes.Structure):
    _fields_ = [
        ('stream_id', ctypes.c_int),
        ('stream_type', ctypes.c_int),
        ('bitrate', ctypes.c_int),
        ('bitrate_pos', ctypes.c_int),
    ]


class mmsh_t(ctypes.Structure):
    _fields_ = [
        ('s', ctypes.c_int),

        ('url', ctypes.c_char_p),
        ('proxy_url', ctypes.c_char_p),
        ('proto', ctypes.c_char_p),
        ('connect_host', ctypes.c_char_p),
        ('connect_port', ctypes.c_int),
        ('http_host', ctypes.c_char_p),
        ('http_port', ctypes.c_int),
        ('http_request_number', ctypes.c_int),
        ('proxy_user', ctypes.c_char_p),
        ('proxy_password', ctypes.c_char_p),
        ('host_user', ctypes.c_char_p),
        ('host_password', ctypes.c_char_p),
        ('uri', ctypes.c_char_p),

        ('str', ctypes.c_char * 1024),  # SCRATCH_SIZE

        ('stream_type', ctypes.c_int),

        ('chunk_type', ctypes.c_ulong),
        ('chunk_length', ctypes.c_ulong),
        ('chunk_seq_number', ctypes.c_ulong),
        ('buf', ctypes.c_ulong * 102400),  # BUF_SIZE

        ('buf_size', ctypes.c_int),
        ('buf_read', ctypes.c_int),

        ('asf_header', ctypes.c_ulong * 8192 * 2),  # ASF_HEADER_SIZE
        ('asf_header_len', ctypes.c_ulong),
        ('asf_header_read', ctypes.c_ulong),
        ('num_stream_ids', ctypes.c_int),
        ('streams', mms_stream_t * 23),  # ASF_MAX_NUM_STREAMS
        ('asf_packet_len', ctypes.c_ulong),
        ('file_len', ctypes.c_longlong),
        ('file_time', ctypes.c_ulonglong),
        ('time_len', ctypes.c_ulonglong),
        ('preroll', ctypes.c_ulonglong),
        ('asf_num_packets', ctypes.c_ulonglong),
        ('guid', ctypes.c_char * 37),

        ('has_audio', ctypes.c_int),
        ('has_video', ctypes.c_int),
        ('seekable', ctypes.c_int),

        ('current_pos', ctypes.c_ulonglong),
        ('bandwidth', ctypes.c_int),
    ]


class MMS(object):
    def __init__(self, url):
        self.libmms = ctypes.cdll.LoadLibrary(ctypes.util.find_library('mms'))
        if self.libmms._name is None:  # pylint:disable=protected-access
            raise download_npo.Error(
                'Deze video is in het (oude) MMS/WMV formaat; om dit te'
                'downloaden heb je libmms nodig, welke niet is gevonden op je'
                'systeem. Zie: http://sourceforge.net/projects/libmms/')

        self._libc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('c'))

        mmsh_connect = self.libmms.mmsh_connect
        mmsh_connect.restype = ctypes.POINTER(mmsh_t)

        if sys.version_info[0] > 2:
            url = bytes(url, 'utf-8')

        self._mms = mmsh_connect(None, None, url, 128 * 1024)

        malloc = self._libc.malloc
        malloc.restype = ctypes.POINTER(ctypes.c_char)
        self.buf = malloc(8192)

    def close(self):
        return self.libmms.mmsh_close(self._mms)

    def read(self, l):
        total = self.libmms.mmsh_read(None, self._mms, self.buf, l)

        if total == 0:
            return None
        return self.buf[0:8192]
