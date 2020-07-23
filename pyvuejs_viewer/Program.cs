using System;
using System.Windows.Forms;
using System.Collections.Generic;
using CefSharp;

namespace pyvuejs_viewer {
    class Program {
        [STAThread]
        static void Main(String[] args) {
            Int32[] geometry = new Int32[]{
                Convert.ToInt32(args[3]),
                Convert.ToInt32(args[4]),
                Convert.ToInt32(args[5]),
                Convert.ToInt32(args[6])
            };

            var settings = new CefSettings();

            WebView view = new WebView(args[0], args[1], args[2], geometry);
            Application.Run(view);
        }
    }
}
