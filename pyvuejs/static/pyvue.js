

var pyvue = {
    // parameters
    __vms: null,
    __name: null,
    __modelNames: null,
    __ws: null,

    // functions
    init: (viewName, modelNames) => {
        this.__vms = {};
        this.__name = viewName;
        this.__modelNames = modelNames;

        this.__ws = new WebSocket(`ws://127.0.0.1:${location.port}/ws`);
        this.__ws.addEventListener("open", (ev) => {
            this.__ws.send(
                JSON.stringify(
                    {
                        job: "open",
                        name: this.__name,
                        state: "success"
                    }
                )
            );

            // pyvue.compute("compute_testVar");
        });
        this.__ws.addEventListener("close", (ev) => {
            try {
                this.__ws.send(
                    JSON.stringify(
                        {
                            job: "close",
                            name: this.__name,
                            state: "sucess"
                        }
                    )
                );
            }
            catch {}
        });
        this.__ws.addEventListener("message", (ev) => {
            var req = JSON.parse(ev.data);
            var res = {
                job: "feedback",
                state: "success"
            };
        
            if (req.job == "init")
            {
                for (var model in req.data) {
                    var methodInfo = {};
                    for (var variable in req.data[model])
                    {
                        var compute = "compute_" + variable;

                        // var computeCode = `console.log("${model}", "${compute}")`;
                        methodInfo[compute] = pyvue.__genMethod(model, compute);
                    }

                    this.__vms[model] = new Vue({
                        el: "#" + model,
                        data: req.data[model],
                        methods: methodInfo
                    });
                }
            }
            else if (req.job == "update")
            {
                if (req.view == this.__name) {
                    if (req.direction == "view")
                    {
                        for (var variable in req.vars) {
                            pyvue.update(req.model, variable, req.vars[variable]);
                        }
                    }
                    else {
                        res["variable"] = {};
                        for (var index in req.variable) {
                            var name = req.variable[index];

                            res.variable[name] = pyvue.get(req.model, name);
                        }
                    }
                }
            }
        
            this.__ws.send(JSON.stringify(res));
        });
    },
    update: (model, variable, value) => {
        var valueString = typeof(value) == "string" ? `"${value}"` : value;
        eval(`this.__vms.${model}.${variable} = ${valueString}`);
    },
    get: (model, variable) => {
        return eval(`this.__vms.${model}.${variable}`);
    },
    compute: (model, method) => {
        this.__ws.send(JSON.stringify(
            {
                job: "compute",
                view: this.__name,
                model: model,
                method: method
            }
        ));
    },
    __genMethod: (model, compute) => {
        return () => {
            pyvue.compute(model, compute);
        }
    }
};
