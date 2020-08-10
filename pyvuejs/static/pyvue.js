
class PyVue {
    $is_init = false;
    $vue = null;
    $ws = null;
    $url = null;
    $selector = null;

    constructor(app_url, selector) {
        this.$url = app_url;
        this.$selector = selector;

        this.$init();

        // setInterval(() => {
        //     axios.get("/server/state").then(() => {
        //         if (!this.$is_init) {
        //             this.$init();
        //         }
        //         document.getElementById("ws_loader").style.display = "none";
        //     }).catch(() => {
        //         this.$is_init = false;
        //         document.getElementById("ws_loader").style.display = "block";
        //     });
        // }, 1000);

        // var ws_url = `ws://${document.domain}:${location.port}${app_url}/`;

        // this.$ws.root = new WebSocket(ws_url + "root");
        // this.$ws.root.onopen = () => {
        //     this.$ws.root.send(JSON.stringify({
        //         state: "connected"
        //     }));
        //     document.getElementById("ws_loader").style.display = "none";
        // };
        // this.$ws.root.onclose = () => {
        //     document.getElementById("ws_loader").style.display = "block";
        // };
        // this.$ws.root.onmessage = (message) => {
        //     var req = JSON.parse(message.data);

        //     var methods = {};
        //     for (var idx in req.methods) {
        //         var method_name = req.methods[idx];
        //         methods[method_name] = this.$generate_method(method_name);
        //     }

        //     this.$vue = new Vue({
        //         el: this.$selector,
        //         data: req.data,
        //         methods: methods
        //     });

        //     this.$ws.data = new WebSocket(ws_url + "data");
        //     // this.$ws.data.onopen = () => {
        //     //     this.$ws.data.send(JSON.stringify({
        //     //         state: "connected",
        //     //         direction: "client"
        //     //     }));
        //     // };
        //     this.$ws.data.onmessage = (message) => {
        //         var req = JSON.parse(message.data);
    
        //         for (var name in req.data) {
        //             this.$set_data(name, req.data[name]);
        //         }
        //     };

        //     this.$ws.methods = new WebSocket(ws_url + "method");
        //     // this.$ws.methods.onopen = () => {
        //     //     this.$ws.methods.send(JSON.stringify({
        //     //         state: "connected"
        //     //     }));
        //     // };
        //     this.$ws.methods.onmessage = (message) => {
        //         var req = JSON.parse(message.data);

        //         this.$ws.data.send(JSON.stringify({
        //             state: "success",
        //             direction: "client"
        //         }));
        //     };
        // };
    }

    $init() {
        axios.get(`/apps${this.$url}/init`).then((response) => {
            var req = response.data;

            var methods = {};
            for (var idx in req.methods) {
                var method_name = req.methods[idx];
                methods[method_name] = this.$generate_method(method_name);
            }

            if (this.$vue == null) {
                this.$vue = new Vue({
                    el: this.$selector,
                    data: req.data,
                    methods: methods,
                    components: req.components
                });
            }
            else {
                this.$vue._data = req.data;
                this.$vue._methods = methods;
            }

            this.$is_init = true;
        })
    }

    $generate_method(method_name) {
        return () => {
            // var send_data = {};
            // for (var name in this.$vue._data) {
            //     send_data[name] = this.$get_data(name);
            // }
            // this.$ws.data.send(JSON.stringify({
            //     state: "success",
            //     direction: "server",
            //     data: send_data
            // }));

            // this.$ws.methods.send(JSON.stringify({
            //     state: "success",
            //     method: method_name
            // }));
            this.$set_data_to_server().then(() => {
                axios.post(`/apps${this.$url}/method`, {
                    method: method_name
                }).then(() => {
                    this.$get_data_from_server();
                });
            });
        }
    }

    $get_data(name) {
        return eval(`this.$vue.${name}`);
    }

    $set_data(name, value) {
        if (typeof(value) == "object") {
            eval(`this.$vue.${name} = value`);
        }
        else {
            var value_string = typeof(value) == "string" ? `"${value}"` : value;
            eval(`this.$vue.${name} = ${value_string}`);
        }
    }

    $get_data_from_server() {
        axios.get(`/apps${this.$url}/data/get`).then((response) => {
            var req = response.data;

            for (var name in req.data) {
                this.$set_data(name, req.data[name]);
            }
        });
    }

    $set_data_to_server() {
        var datas = {};
        for (var name in this.$vue._data) {
            datas[name] = this.$vue._data[name];
        }

        return axios.post(`/apps${this.$url}/data/set`, {
            data: datas
        });
    }
};