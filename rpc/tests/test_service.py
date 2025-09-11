import pytest
import asyncio

from lib.encoding import Enc, InvalidTypeError, Tup2
from lib.service import Desc, decl, add, find, BadArityError
import lib.jsonrpc as jsonrpc

# -------------------------
# Tests encoding.py
# -------------------------

def test_basic_encodings():
    # Bool
    b = True
    assert Enc.bool.val_to_json(b) == True
    assert Enc.bool.val_of_json(True) == True
    with pytest.raises(InvalidTypeError):
        Enc.bool.val_of_json("not bool")

    # Int
    i = 42
    assert Enc.int.val_to_json(i) == 42
    assert Enc.int.val_of_json(42) == 42
    with pytest.raises(InvalidTypeError):
        Enc.int.val_of_json(True)  # bool is not int

    # Option
    opt = Enc.option_of(Enc.int)
    assert opt.val_of_json({"None": None}) is None
    assert opt.val_of_json({"Some": 123}) == 123
    assert opt.val_to_json(None) == {"None": None}
    assert opt.val_to_json(456) == {"Some": 456}

    # Tup2
    tup = Tup2(Enc.int, Enc.string)
    j = [1, "a"]
    assert tup.val_of_json(j) == (1, "a")
    assert tup.val_to_json((2, "b")) == [2, "b"]


# -------------------------
# Tests jsonrpc.py
# -------------------------

def test_id_serialization():
    for val in [42, "abc"]:
        j = jsonrpc.id_to_json(val)
        v = jsonrpc.id_from_json(j)
        assert v == val

    with pytest.raises(ValueError):
        jsonrpc.id_from_json(3.14)  # invalid type

def test_notification_serialization():
    notif = jsonrpc.Notification(method="test", params={"x": 1})
    j = notif.to_json()
    n2 = jsonrpc.Notification.from_json(j)
    assert n2.method == "test"
    assert n2.params == {"x": 1}

def test_request_serialization():
    req = jsonrpc.Request(id=1, method="add", params=[1,2])
    j = req.to_json()
    r2 = jsonrpc.Request.from_json(j)
    assert r2.id == 1
    assert r2.method == "add"
    assert r2.params == [1,2]


# -------------------------
# Tests service.py
# -------------------------

@pytest.mark.asyncio
async def test_desc_eval_sync():
    # Simple return R
    async def f(): return 10
    d = Desc.R(Enc.int)
    result = await d.eval(f, [])
    assert result == 10

@pytest.mark.asyncio
async def test_desc_eval_nested():
    async def add_one(x): return lambda: x + 1
    d = Desc.N(Enc.int, Desc.R(Enc.int))
    result = await d.eval(add_one, [5])
    assert result == 6

@pytest.mark.asyncio
async def test_bad_arity():
    async def f(): return 1
    d = Desc.R(Enc.int)
    with pytest.raises(BadArityError):
        await d.eval(f, [1])  # too many args


def test_service_add_find():
    async def f(): return "ok"
    m = decl("m1", Desc.R(Enc.string), f)
    svc = add({}, m)
    desc, func = find(svc, "m1")
    assert desc is not None
    assert asyncio.iscoroutinefunction(func)
