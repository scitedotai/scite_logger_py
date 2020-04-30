import logging

import scite_logger_py as logger


def test_CustomJsonFormatter_adds_metadata(mocker):
    timestamp = "bingbong"
    datetime = mocker.patch("scite_logger_py.datetime")
    datetime.utcnow.return_value.strftime.return_value = timestamp

    pid = 1234
    mocker.patch("os.getpid", return_value=pid)

    load = 0.3
    mocker.patch("os.getloadavg", return_value=[load])

    mem = 34
    virtual_memory = mocker.patch("psutil.virtual_memory")
    virtual_memory.return_value.available = mem

    u_id = 'unique-string'
    uuid4 = mocker.patch("uuid.uuid4")
    uuid4.return_value.hex = u_id

    called_by = 'Tim'
    mocker.patch("inspect.stack", return_value=[
        [None, called_by]
    ])

    formatter = logger.CustomJsonFormatter()
    log_record = {}
    record = mocker.MagicMock()
    record.levelname = 'EMERGENCY_BROADCAST'
    formatter.add_fields(log_record, record, {})

    assert log_record == {
        'message': None,
        'method_calls': [],
        'timestamp': timestamp,
        'log': {
            'level': 'EMERGENCY_BROADCAST'
        },
        'process': {
            'pid': pid
        },
        'machine': {
            'load': load,
            'mem': mem
        },
        'host': {},
        'called_by': called_by,
        'u_id': u_id
    }, "expected log_record"


def test_CustomJsonFormatter_exc_info(mocker):
    error_msg = "Oh no I broke"
    formatter = logger.CustomJsonFormatter()
    log_record = {
        'exc_info': error_msg
    }
    formatter.add_fields(log_record, mocker.MagicMock(), {})
    assert log_record['error']['message'] == error_msg,\
        "Right error message added"


def test_CustomJsonFormatter_name(mocker):
    service_name = "trusty_lib"
    formatter = logger.CustomJsonFormatter()
    log_record = {
        'name': service_name
    }
    formatter.add_fields(log_record, mocker.MagicMock(), {})
    assert 'name' not in log_record, "Original name removed"
    assert log_record['service']['name'] == service_name,\
        "Name moved to correct place"


def test_create_logger(mocker):
    log_handler = mocker.MagicMock()
    formatter = "my_formatter"
    log_path = "path/to/app.log"
    log_level = logging.DEBUG

    makedirs = mocker.patch("os.makedirs")
    mocker.patch("logging.getLogger")
    mocker.patch(
        "scite_logger_py.CustomJsonFormatter",
        return_value=formatter
    )

    my_logger = logger.create_logger(
        log_handler=log_handler,
        log_level=log_level,
        log_path=log_path
    )

    # Does not create directory
    makedirs.assert_called_with("path/to", exist_ok=True)

    # Does not set formatter
    log_handler.setFormatter.assert_called_with(formatter)

    # adds StreamHandler
    my_logger.addHandler.assert_called_with(log_handler)

    # sets expected level
    my_logger.setLevel.assert_called_with(log_level)
