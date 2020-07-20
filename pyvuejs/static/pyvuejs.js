
var pyvuejs = {
    // parameters
    __vms: null,
    __id: null,
    __name: null,
    __prefix: null,
    __modelNames: null,
    __template: null,
    __ws: null,

    // functions
    init: (viewId, viewName, viewPrefix, modelNames, template) => {
        this.__vms = {};
        this.__id = viewId;
        this.__name = viewName;
        this.__prefix = viewPrefix;
        this.__modelNames = modelNames;
        this.__template = template;

        this.__ws = new WebSocket(`ws://127.0.0.1:${location.port}/ws`);
        this.__ws.addEventListener("open", (ev) => {
            pyvuejs.open(this.__id, this.__name);
        });
        this.__ws.addEventListener("close", (ev) => {
            pyvuejs.close(this.__id, this.__name);
        });
        this.__ws.addEventListener("message", (ev) => {
            var req = JSON.parse(ev.data);
            var res = {
                job: "feedback",
                state: "success"
            };
        
            if (req.job == "init")
            {
                if (this.__id == req.id) {
                    for (var model in req.data) {
                        var vm_data = req.data[model];
                        vm_data["session"] = req.data.session;

                        var computeInfo = {};
                        for (var idx in req.computes[model]) {
                            var compute = req.computes[model][idx];
                            computeInfo[compute] = pyvuejs.__genMethod(model, "compute", compute);
                        }

                        var methodInfo = {};
                        for (var idx in req.methods[model]) {
                            var method = req.methods[model][idx];
                            methodInfo[method] = pyvuejs.__genMethod(model, "method", method);
                        }
    
                        this.__vms[model] = new Vue({
                            el: "#" + model,
                            data: req.data[model],
                            computed: computeInfo,
                            methods: methodInfo
                        });
                    }
                }
            }
            else if (req.job == "update")
            {
                if (req.id == this.__id && req.view == this.__name) {
                    if (req.direction == "view")
                    {
                        for (var variable in req.vars) {
                            pyvuejs.update(req.model, variable, req.vars[variable]);
                        }
                    }
                    else {
                        res["variable"] = {};
                        for (var index in req.variable) {
                            var name = req.variable[index];

                            res.variable[name] = pyvuejs.get(req.model, name);
                        }
                    }
                }
            }
        
            res["id"] = this.__id;
            this.__ws.send(JSON.stringify(res));
        });
    },
    update: (model, variable, value) => {
        if (variable == "session") {
            for (var varName in value) {
                var varReal = value[varName];
                var valueString = typeof(varReal) == "string" ? `"${varReal}"` : varReal;

                eval(`this.__vms.session.${varName} = ${valueString}`);
            }
        }
        else {
            var valueString = typeof(value) == "string" ? `"${value}"` : value;
            eval(`this.__vms.${model}.${variable} = ${valueString}`);
        }
    },
    get: (model, variable) => {
        return eval(`this.__vms.${model}.${variable}`);
    },
    compute: (model, compute) => {
        this.__ws.send(JSON.stringify(
            {
                job: "compute",
                id: this.__id,
                view: this.__name,
                model: model,
                compute: compute
            }
        ));

        // var iframes = document.getElementsByTagName("iframe");
        // for (var idx = 0; idx < iframes.length; idx++) {
        //     iframes[idx].contentWindow.location.reload(true);
        // }
    },
    method: (model, method) => {
        this.__ws.send(JSON.stringify(
            {
                job: "method",
                id: this.__id,
                view: this.__name,
                model: model,
                method: method
            }
        ));
    },
    open: (id, name) => {
        this.__ws.send(
            JSON.stringify(
                {
                    job: "open",
                    state: "success",
                    id: id == undefined || id == null ? "null" : id,
                    name: name
                }
            )
        );
    },
    close: (id, name) => {
        this.__ws.send(
            JSON.stringify(
                {
                    job: "close",
                    id: id,
                    name: name,
                    state: "sucess"
                }
            )
        );
    },
    __genMethod: (model, fType, fName) => {
        if (fType == "compute") {
            return () => {
                pyvuejs.compute(model, fName);
            }
        }
        else {
            return () => {
                pyvuejs.method(model, fName);
            }
        }
    }
};
