# Streaming SDK For TaoBao
from datetime import datetime
from hashlib import md5
import httplib
from socket import timeout
from threading import Thread
from time import sleep
import urllib


STREAM_VERSION = '0.1'


class StreamListener(object):
    def __init__(self, api=None):
        pass

    def on_message(self, data):
        """Called On Normal Message arrives"""
        raise NotImplementedError()

    def on_heartbeat(self):
        """Called On Heartbeat Message arrives"""
        raise NotImplementedError()

    def on_timeout(self):
        """Called when stream connection times out"""
        raise NotImplementedError()

    def on_error(self, data):
        """Called when stream connection times out"""
        raise NotImplementedError()


class Stream(object):
    uri = '/stream'

    def __init__(self, listener, **options):
        self.listener = listener
        self.running = False
        self.timeout = options.get("timeout", 300.0)
        self.retry_count = options.get("retry_count")
        self.retry_time = options.get("retry_time", 10.0)
        self.snooze_time = options.get("snooze_time", 5.0)
        self.buffer_size = options.get("buffer_size", 1500)
        self.host = options.get('host', 'stream.api.taobao.com')

        self.headers = options.get("headers") or {}
        self.parameters = None

        app_key = options.get('app_key', None)
        app_sec = options.get('app_sec', None)

        if not app_key or not app_sec:
            raise RuntimeError('no app_key or app_sec configured')

        self.query = self._init_body(app_key, app_sec)

    def _init_body(self, app_key, app_sec):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        args = dict(app_key=app_key, timestamp=ts)

        sign = md5(
            app_sec + ''.join(
                ['%s%s' % (k, args[k]) for k in sorted(args.keys())]
            ) + app_sec
        ).hexdigest().upper()

        args['sign'] = sign
        return urllib.urlencode(args)

    def _run(self):
        # Connect and process the stream
        error_counter = 0
        conn = None
        exception = None
        while self.running:
            if self.retry_count is not None and error_counter > self.retry_count:
                # quit if error count greater than retry count
                break
            try:
                conn = httplib.HTTPConnection(self.host)
                conn.connect()
                conn.sock.settimeout(self.timeout)
                conn.request('POST', self.uri + '?' + self.query, None, headers=self.headers)
                resp = conn.getresponse()
                if resp.status != 200:
                    if self.listener.on_error(resp.status) is False:
                        break
                    error_counter += 1
                    sleep(self.retry_time)
                else:
                    error_counter = 0
                    self._read_loop(resp)
            except timeout:
                if not self.listener.on_timeout():
                    break
                if self.running is False:
                    break
                conn.close()
                sleep(self.snooze_time)
            except Exception, e:
                # any other exception is fatal, so kill loop
                print e.message

        # cleanup
        self.running = False
        if conn:
            conn.close()

        if exception:
            raise

    def _read_loop(self, resp):
        while self.running and not resp.isclosed():
            # Note: keep-alive newlines might be inserted before each length value.
            # read until we get a digit...
            c = '\n'
            while c == '\n' and self.running and not resp.isclosed():
                c = resp.read(1)
            delimited_string = c
            # read rest of delimiter length..
            d = ''
            while d != '\n' and self.running and not resp.isclosed():
                d = resp.read(1)
                delimited_string += d
            self.listener.on_message(delimited_string.strip())
        if resp.isclosed():
            self.on_closed(resp)

    def _start(self, sync=True):
        self.running = True
        if not sync:
            Thread(target=self._run).start()
        else:
            self._run()

    def on_closed(self, resp):
        """ Called when the response has been closed by TaoBao """
        pass

    def disconnect(self):
        if self.running is False:
            return
        self.running = False

    def run(self):
        self._start()
