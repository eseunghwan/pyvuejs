
class pyvuejs {
    constructor(id, name, prefix, models) {
        this.__vms = {};
        this.__id = id;
        this.__name = name;
        this.__prefix = prefix;
        this.__models = models;
        this.__socketio = null;
        this.__sessionTick = null;
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

    __compute(model, compute) {
        var variables = {};
        for (var varName in this.__vms[model]._data) {
            if (varName != "session") {
                variables[varName] = this.__get(model, varName);
            }
        }
        this.__socketio.emit("compute", {
            id: this.__id,
            name: this.__name,
            model: model,
            variables: variables,
            session: this.__get(model, "session"),
            compute: compute
        });
    }

    __method(model, method) {
        var variables = {};
        for (var varName in this.__vms[model]._data) {
            if (varName != "session") {
                variables[varName] = this.__get(model, varName);
            }
        }
        this.__socketio.emit("method", {
            id: this.__id,
            name: this.__name,
            model: model,
            variables: variables,
            session: this.__get(model, "session"),
            method: method
        });
    }

    __update(model, variable, value)  {
        if (typeof(value) == "object") {
            eval(`this.__vms.${model}.${variable} = value`);
        }
        else {
            var valueString = typeof(value) == "string" ? `"${value}"` : value;
            eval(`this.__vms.${model}.${variable} = ${valueString}`);
        }
    }

    __get(model, variable) {
        return eval(`this.__vms.${model}.${variable}`);
    }

    __upload_session(sessionData) {
        var req = new XMLHttpRequest();
        req.open("POST", `http://${document.domain}:${location.port}/session/upload`);
        req.send(JSON.stringify({
            id: this.__id,
            name: this.__name,
            session: sessionData
        }));
    }

    __download_session(viewId, viewName, vms) {
        var req = new XMLHttpRequest();
        req.onreadystatechange = () => {
            if (req.readyState == XMLHttpRequest.DONE && req.status == 200) {
                var res = JSON.parse(req.responseText);

                if (res.id == viewId && res.excludeName != viewName) {
                    for (var model in vms) {
                        vms[model].session = res.sessions[viewId][viewName][model];
                    }
                }
            }
        };
        req.open("POST", `http://${document.domain}:${location.port}/session/download`);
        req.send(JSON.stringify({ id: this.__id }));
    }

    init() {
        console.log(this.__id, this.__name);
        this.__socketio = io.connect(`http://${document.domain}:${location.port}/pyvuejsSocket`);
        this.__socketio.on("feedbackJS", (res) => {
            if (res.job == "connect") {
                this.__socketio.emit("initViewPY", {
                    job: "initView",
                    id: this.__id,
                    name: this.__name
                });
            }
        });
        this.__socketio.on("initViewJS", (res) => {
            if (res.id == this.__id && res.name == this.__name) {
                for (var mIdx in this.__models) {
                    var model = this.__models[mIdx];
    
                    var vm_data = res.data[model];
                    vm_data["session"] = res.session;
    
                    var computeInfo = {};
                    for (var idx in res.computes[model]) {
                        var compute = res.computes[model][idx];
                        computeInfo[compute] = this.__genMethod(model, "compute", compute);
                    }
    
                    var methodInfo = {};
                    for (var idx in res.methods[model]) {
                        var method = res.methods[model][idx];
                        methodInfo[method] = this.__genMethod(model, "method", method);
                    }
    
                    this.__vms[model] = new Vue({
                        el: "#" + model,
                        data: vm_data,
                        computed: computeInfo,
                        methods: methodInfo
                    });
                    this.__upload_session(res.session);
                }
            }
        });
        this.__socketio.on("update", (res) => {
            if (res.id == this.__id && res.name == this.__name) {
                for (var varName in res.variables) {
                    this.__update(res.model, varName, res.variables[varName]);
                }

                for (var mIdx in this.__models) {
                    this.__update(this.__models[mIdx], "session", res.session);
                }

                this.__upload_session(res.session);
            }
        });
        this.__socketio.on("updateSessionJS", (res) => {
            if (res.id == this.__id && res.name == this.__name) {
                for (var mIdx in this.__models) {
                    console.log(res.name, this.__models[mIdx]);
                    this.__update(this.__models[mIdx], "session", res.session);
                }

                this.__socketio.emit("feedbackPY", {
                    job: "updateSessionJS",
                    state: "success"
                });
            }
        });

        this.__sessionTick = setInterval(this.__download_session, 100, this.__id, this.__name, this.__vms);
        // this.__ws.addEventListener("open", (ev) => {
        //     this.__ws.send(
        //         JSON.stringify(
        //             {
        //                 job: "open",
        //                 state: "success",
        //                 id: this.__id,
        //                 name: this.__name
        //             }
        //         )
        //     );
        // });
        // this.__ws.addEventListener("message", (ev) => {
        //     var req = JSON.parse(ev.data);
        //     var res = {
        //         job: "feedback",
        //         state: "success"
        //     };
        
        //     if (req.job == "init")
        //     {
        //         if (req.id == this.__id && req.name == this.__name) {
        //             for (var mIdx in this.__models) {
        //                 var model = this.__models[mIdx];
        //                 if (req.data[model] != undefined) {
        //                     var vm_data = req.data[model];
        //                     vm_data["session"] = req.session;

        //                     var computeInfo = {};
        //                     for (var idx in req.computes[model]) {
        //                         var compute = req.computes[model][idx];
        //                         computeInfo[compute] = this.__genMethod(model, "compute", compute);
        //                     }

        //                     var methodInfo = {};
        //                     for (var idx in req.methods[model]) {
        //                         var method = req.methods[model][idx];
        //                         methodInfo[method] = this.__genMethod(model, "method", method);
        //                     }

        //                     sessionStorage.setItem("appSession", req.session);
        //                     this.__vms[model] = new Vue({
        //                         el: "#" + model,
        //                         data: vm_data,
        //                         computed: computeInfo,
        //                         methods: methodInfo
        //                     });
        //                 }
        //             }
        //         }
        //     }
        //     else if (req.job == "update")
        //     {
        //         if (req.id == this.__id && req.view == this.__name) {
        //             if (this.__models.indexOf(req.model) != -1) {
        //                 if (req.direction == "view")
        //                 {
        //                     for (var variable in req.vars) {
        //                         this.__update(req.model, variable, req.vars[variable]);
        //                     }
        //                     console.log(this.__name, req.session);
        //                     this.__update(req.model, "session", req.session);
        //                 }
        //                 else {
        //                     res["variable"] = {};
        //                     for (var index in req.variable) {
        //                         var name = req.variable[index];

        //                         res.variable[name] = this.__get(req.model, name);
        //                     }

        //                     res["session"] = this.__vms[req.model].session;
        //                 }
        //             }
        //         }
        //     }
        
        //     res["id"] = this.__id;
        //     this.__ws.send(JSON.stringify(res));
        // });
    }
}
