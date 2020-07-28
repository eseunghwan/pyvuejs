
class pyvuejs {
    constructor(id, name, models) {
        this.__vms = {};
        this.__id = id;
        this.__name = name;
        this.__models = models;
        this.__socketio = null;
        this.__sessionTick = null;
    }

    genMethod(model, fName) {
        return () => {
            this.method(model, fName);
        }
    }

    method(model, method) {
        this.__stop_session_refresh();
        this.upload_variable();

        this.__do_request("POST", "/functions/method", {
            id: this.__id,
            name: this.__name,
            model: model,
            method: method
        }, (res) => {
            if (res.state == "success") {
                this.download_variable();
                this.__start_session_refresh();
            }
        });
    }

    update(model, variable, value)  {
        if (typeof(value) == "object") {
            eval(`this.__vms.${model}.${variable} = value`);
        }
        else {
            var valueString = typeof(value) == "string" ? `"${value}"` : value;
            eval(`this.__vms.${model}.${variable} = ${valueString}`);
        }
    }

    get(model, variable) {
        return eval(`this.__vms.${model}.${variable}`);
    }

    __do_request(method, url, req_data, req_method) {
        var req = new XMLHttpRequest();
        req.onreadystatechange = () => {
            if (req.readyState == XMLHttpRequest.DONE && req.status == 200) {
                req_method(JSON.parse(req.responseText));
            }
        }

        req.open(method, url);
        req.send(JSON.stringify(req_data));
    }

    upload_variable() {
        var variable_data = {};
        for (var model in this.__vms) {
            variable_data[model] = {};
            for (var var_name in this.__vms[model]._data) {
                if (var_name != "session") {
                    variable_data[model][var_name] = this.get(model, var_name);
                }
            }
        }

        this.__do_request("POST", "/functions/upload_variable", {
            id: this.__id,
            name: this.__name,
            variable: variable_data
        }, (res) => {
            if (res.state == "success") {
                log("info", `View ${this.__id}/${this.__name} variables uploaded`);
            }
        });
    }

    download_variable() {
        this.__do_request("POST", "/functions/download_variable", {
            id: this.__id,
            name: this.__name
        }, (res) => {
            if (res.state == "success") {
                for (var model in res.variable) {
                    for (var var_name in res.variable[model]) {
                        this.update(model, var_name, res.variable[model][var_name]);
                    }
                }

                log("info", `View ${this.__id}/${this.__name} variables downloaded`);
            }
        });
    }

    upload_session() {
        var session_data;
        for (var model in this.__vms) {
            session_data = this.get(model, "session");
            break;
        }

        this.__do_request("POST", "/functions/upload_session", {
            id: this.__id,
            name: this.__name,
            session: session_data
        }, (res) => {
            if (res.state == "success") {
                log("info", `View ${this.__id}/${this.__name} session uploaded`);
            }
        });
    }

    download_session() {
        this.__do_request("POST", "/functions/download_session", { id: this.__id }, (res) => {
            if (res.state == "success") {
                for (var model in this.__vms) {
                    this.update(model, "session", res.session);
                }

                log("info", `View ${this.__id}/${this.__name} session downloaded`);
            }
        });
    }

    __start_session_refresh() {
        this.__sessionTick = setInterval(this.__download_session_interval, 500, this.__id, this.__vms);
    }

    __stop_session_refresh() {
        clearInterval(this.__sessionTick);
    }

    __download_session_interval(view_id, vm_info) {
        var req = new XMLHttpRequest();
        req.onreadystatechange = () => {
            if (req.readyState == XMLHttpRequest.DONE && req.status == 200) {
                var res = JSON.parse(req.responseText);
                if (res.state == "success") {
                    for (var model in vm_info) {
                        vm_info[model].session = res.session;
                    }
                }
            }
        }

        req.open("POST", "/functions/download_session");
        req.send(JSON.stringify({ id: view_id }));
    }

    init() {
        this.__do_request("POST", "/functions/init_view", {
            "id": this.__id,
            "name": this.__name
        }, (res) => {
            if (res.state == "success") {
                for (var mIdx in this.__models) {
                    var model = this.__models[mIdx];
    
                    var vm_data = res.data[model];
                    vm_data["session"] = res.session;
    
                    var methodInfo = {};
                    for (var idx in res.methods[model]) {
                        var method = res.methods[model][idx];
                        methodInfo[method] = this.genMethod(model, method);
                    }
    
                    this.__vms[model] = new Vue({
                        el: "#" + model,
                        data: vm_data,
                        methods: methodInfo,
                    });
                    // this.download_session();
                    log("info", `Model ${this.__id}/${this.__name}/${model} created`);

                    this.__start_session_refresh()
                }

                log("info", `View ${this.__id}/${this.__name} loaded`);
            }
        });
    }
}
