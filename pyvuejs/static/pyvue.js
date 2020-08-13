
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
    }

    $init() {
        axios.get(`${this.$url}/init`).then((response) => {
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
                axios.post(`${this.$url}/method`, {
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
        axios.get(`${this.$url}/data/get`).then((response) => {
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

        return axios.post(`${this.$url}/data/post`, {
            data: datas
        });
    }
};