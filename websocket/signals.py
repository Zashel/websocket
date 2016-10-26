from zashel.signal import Signal, MetaSignal
import datetime
import json

class WebSocketSignal(Signal):
    classes = dict()
    @classmethod
    def _insert_new_class(cls, name, obj):
        WebSocketSignal.classes[name] = obj
        
    @classmethod
    def get_class(cls, name):
        return WebSocketSignal.classes[name]

class WebSocketMetaSignal(MetaSignal):
    def __new__(cls, action, arg_names=list(), arg_types=list(), *, parent=WebSocketSignal):
        meta = MetaSignal(action, arg_names, arg_types, parent=parent)
        def to_json(self):
            result = {
                    "signal": action,
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
            result.update(dict(
                    zip(
                            arg_names,
                            self.args
                            )
                    ))
            return json.dumps(result)
        setattr(meta, "to_json", to_json)
        WebSocketSignal._insert_new_class(action, meta)
        return meta

    def __init__(cls, action, arg_names=list(), arg_types=list(), *, parent=WebSocketSignal):
        cls.__init__(cls, action, arg_names, arg_types, parent=parent)


def from_json(event):
    data = json.loads(event)
    if data["signal"] in WebSocketSignal.classes:
        signal = WebSocketSignal.classes[data["signal"]]
        args = signal.arg_names
        return signal(*[data[name] for name in args])
    else:
        return None

#Signals
ByeSignal = WebSocketMetaSignal("bye")
PingSignal = WebSocketMetaSignal("ping")
PongSignal = WebSocketMetaSignal("pong")
MessageSignal = WebSocketMetaSignal("message", ("to", "text"), (str, str))
