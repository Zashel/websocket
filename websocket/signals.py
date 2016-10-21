from zashel.signal import Signal, MetaSignal
import datetime
import json

class WebSocketSignal(MetaSignal):
    def __new__(cls, action, arg_names=list(), arg_types=list()):
        meta = super().__new__(cls, action, arg_names, arg_types)
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
        return meta
