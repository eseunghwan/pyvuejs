
class pyvuejs {
    constructor(id, name, prefix, models) {
        this.__vms = {};
        this.__id = id;
        this.__name = name;
        this.__prefix = prefix;
        this.__models = models;
        this.__ws = new WebSocket(`ws://127.0.0.1:${location.port}/ws`);
    }

    __genMethod(model, fType, fName) {
        if (fType == "compute") {
            return () => {
                this.__compute(model, fName);
            }
        }
        else {
            return () => {
                this.__method(model, fName);
            }
        }
    }

    init() {
        this.__ws.addEventListener("open", (ev) => {
            this.__ws.send(
                JSON.stringify(
                    {
                        job: "open",
                        state: "success",
                        id: this.__id,
                        name: this.__name
                    }
                )
            );
        });
        this.__ws.addEventListener("message", (ev) => {
            var req = JSON.parse(ev.data);
            var res = {
                job: "feedback",
                state: "success"
            };
        
            if (req.job == "init")
            {
                if (req.id == this.__id && req.name == this.__name) {
                    for (var mIdx in this.__models) {
                        var model = this.__models[mIdx];
                        if (req.data[model] != undefined) {
                            var vm_data = req.data[model];
                            vm_data["session"] = req.session;

                            var computeInfo = {};
                            for (var idx in req.computes[model]) {
                                var compute = req.computes[model][idx];
                                computeInfo[compute] = this.__genMethod(model, "compute", compute);
                            }

                            var methodInfo = {};
                            for (var idx in req.methods[model]) {
                                var method = req.methods[model][idx];
                                methodInfo[method] = this.__genMethod(model, "method", method);
                            }
        
                            this.__vms[model] = new Vue({
                                el: "#" + model,
                                data: vm_data,
                                computed: computeInfo,
                                methods: methodInfo
                            });
                        }
                    }
                }
            }
            else if (req.job == "update")
            {
                if (req.id == this.__id && req.view == this.__name) {
                    if (this.__models.indexOf(req.model) != -1) {
                        if (req.direction == "view")
                        {
                            for (var variable in req.vars) {
                                this.__update(req.model, variable, req.vars[variable]);
                            }
                        }
                        else {
                            res["variable"] = {};
                            for (var index in req.variable) {
                                var name = req.variable[index];

                                res.variable[name] = this.__get(req.model, name);
                            }
                        }
                    }
                }
            }
        
            res["id"] = this.__id;
            this.__ws.send(JSON.stringify(res));
        });
    }

    __update(model, variable, value)  {
        if (variable == "session") {
            for (var varName in value) {
                var varReal = value[varName];

                if (typeof(varReal) == "object") {
                    eval(`this.__vms.${model}.session.${varName} = varReal`);
                }
                else {
                    var valueString = typeof(varReal) == "string" ? `"${varReal}"` : varReal;
                    eval(`this.__vms.${model}.session.${varName} = ${valueString}`);
                }
            }
        }
        else {
            if (typeof(value) == "object") {
                eval(`this.__vms.${model}.${variable} = value`);
            }
            else {
                var valueString = typeof(value) == "string" ? `"${value}"` : value;
                eval(`this.__vms.${model}.${variable} = ${valueString}`);
            }
        }
    }

    __get(model, variable) {
        return eval(`this.__vms.${model}.${variable}`);
    }

    __compute(model, compute) {
        this.__ws.send(JSON.stringify(
            {
                job: "compute",
                id: this.__id,
                view: this.__name,
                model: model,
                compute: compute
            }
        ));
    }

    __method(model, method) {
        this.__ws.send(JSON.stringify(
            {
                job: "method",
                id: this.__id,
                view: this.__name,
                model: model,
                method: method
            }
        ));
    }
}
