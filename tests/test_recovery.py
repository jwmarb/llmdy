from mock import MagicMock, mock_open, patch, Mock
import llmdy
import os
import fakeredis


class TestFile:
    __test__ = False

    def __init__(self):
        self.path = os.path.join(os.curdir, "tests", "test_file")
        self.tmp_path = self.path + ".tmp"

    def remove(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.remove()


def test_disk_recovery_initial():
    # Should work fine; good to check if this module is tightly coupled
    llmdy.recovery.RECOVERY_STRATEGY = "disk"

    with TestFile() as file:
        recovery = llmdy.recovery.Recovery(key=file.path, url=file.path)

        assert recovery.recover() == ""


def test_disk_recovery_strategy():
    # Should work fine; good to check if this module is tightly coupled
    llmdy.recovery.RECOVERY_STRATEGY = "disk"
    with TestFile() as file:
        recovery = llmdy.recovery.Recovery(key=file.path, url=file.path)

        with patch('builtins.open', mock_open()) as _mocked:
            mocked: Mock = _mocked

            mock_file = MagicMock()
            mocked.return_value = mock_file

            with recovery as r:
                # Check __enter__
                mocked.assert_called_with(file.tmp_path, "a+")

                r.write("Hello")
                assert r._data == "Hello"
                mock_file.write.assert_called_with("Hello")

                r.write(" World")
                assert r._data == "Hello World"
                mock_file.write.assert_called_with(" World")

            # Check __exit__
            mocked.assert_called_with(file.path, "w+")
            assert r._data == None


def test_disk_recovery_strategy_with_interrupted_write():
    # Should work fine; good to check if this module is tightly coupled
    llmdy.recovery.RECOVERY_STRATEGY = "disk"

    on_complete_write = MagicMock(return_value="Hello World! Done.")

    with TestFile() as file:
        recovery = llmdy.recovery.Recovery(
            key=file.path, url=file.path, on_complete_write=on_complete_write)
        try:
            with recovery as r:
                r.write("Hello ")
                raise Exception("mock")
        except Exception as e:
            # Make sure this is the correct exception
            assert str(e) == "mock"
            assert os.path.exists(file.tmp_path)
        finally:
            assert recovery.recover() == "Hello "

        # append changes to file and see if it doesnt overwrite existing contents
        try:
            with recovery as r:
                r.write("World!")
                raise Exception("mock")
        except Exception as e:
            # Make sure this is the correct exception
            assert str(e) == "mock"
            assert os.path.exists(file.tmp_path)
        finally:
            assert recovery.recover() == "Hello World!"

        with recovery as r:
            r.write(" Done.")

        assert not os.path.exists(file.tmp_path)
        assert os.path.exists(file.path)

        on_complete_write.assert_called_once_with("Hello World! Done.")


def test_redis_recovery_initial():
    # Should work fine; good to check if this module is tightly coupled
    llmdy.recovery.RECOVERY_STRATEGY = "redis"

    recovery = llmdy.recovery.Recovery(key="", url="redis")

    assert recovery.recover() == ""


def test_redis_recovery_strategy():
    # Should work fine; good to check if this module is tightly coupled
    llmdy.recovery.RECOVERY_STRATEGY = "redis"
    redis = fakeredis.FakeRedis(server_type="redis")
    llmdy.recovery.rediscli = redis

    with TestFile() as file:
        recovery = llmdy.recovery.Recovery(key=file.path, url=file.path)

        with recovery as r:
            r.write("hello")
            assert redis.get(recovery._prog_key) == b'hello'

            r.write(" world")
            assert redis.get(recovery._prog_key) == b'hello world'

        assert redis.get(recovery._prog_key) == None
        assert redis.get(recovery._key) == b'hello world'


def test_redis_recovery_strategy_with_interrupted_write():
    # Should work fine; good to check if this module is tightly coupled
    llmdy.recovery.RECOVERY_STRATEGY = "redis"
    redis = fakeredis.FakeRedis(server_type="redis")
    llmdy.recovery.rediscli = redis

    with TestFile() as file:
        recovery = llmdy.recovery.Recovery(key=file.path, url=file.path)

        try:
            with recovery as r:
                r.write("hello")
                assert redis.get(recovery._prog_key) == b'hello'
                raise Exception("mock")
        except Exception as e:
            assert str(e) == "mock"
            assert recovery.recover() == "hello"
            assert redis.get(recovery._prog_key) == b"hello"
            assert len(redis.keys()) == 1

        with recovery as r:
            r.write(" world")
            assert redis.get(recovery._prog_key) == b'hello world'

        assert redis.get(recovery._key) == b'hello world'
        assert len(redis.keys()) == 1


def test_none_recovery_initial():
    # Should work fine; good to check if this module is tightly coupled
    llmdy.recovery.RECOVERY_STRATEGY = "none"
    redis = fakeredis.FakeRedis(server_type="redis")
    llmdy.recovery.rediscli = redis

    with TestFile() as file:
        recovery = llmdy.recovery.Recovery(key=file.path, url=file.path)

        with patch("builtins.open", mock_open()) as _mocked:
            mocked: Mock = _mocked
            assert recovery.recover() == ''
            assert redis.keys() == []
            mocked.assert_not_called()


def test_none_recovery_strategy():
    # Should work fine; good to check if this module is tightly coupled
    llmdy.recovery.RECOVERY_STRATEGY = "none"
    redis = fakeredis.FakeRedis(server_type="redis")
    llmdy.recovery.rediscli = redis

    with TestFile() as file:
        recovery = llmdy.recovery.Recovery(key=file.path, url=file.path)

        def assert_none_called():
            assert redis.keys() == []
            mocked.assert_not_called()

        with patch("builtins.open", mock_open()) as _mocked:
            mocked: Mock = _mocked
            file_mock = MagicMock()
            mocked.return_value.__enter__.return_value = file_mock

            with recovery as r:
                r.write("hello world!")
                assert_none_called()

            mocked.assert_called_once_with(recovery._file_path, "w+")
            file_mock.write.assert_called_with("hello world!")
            assert recovery._data == None

        # Should technically reset because there is no recovery
        assert recovery.recover() == ""


def test_none_recovery_strategy():
    # Should work fine; good to check if this module is tightly coupled
    llmdy.recovery.RECOVERY_STRATEGY = "none"
    redis = fakeredis.FakeRedis(server_type="redis")
    llmdy.recovery.rediscli = redis

    with TestFile() as file:
        recovery = llmdy.recovery.Recovery(key=file.path, url=file.path)

        try:
            with recovery as r:
                r.write("hello ")
                assert not os.path.exists(file.path)
                raise Exception("mock")
        except Exception as e:
            assert str(e) == "mock"
            assert not os.path.exists(file.path)
            assert recovery.recover() == ""

        with recovery as r:
            r.write("world!")

        assert recovery.recover() == ''  # Nothing to recover
