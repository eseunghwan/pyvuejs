using System;
using System.Windows.Forms;

using CefSharp;
using CefSharp.WinForms;

namespace pyvuejs_viewer
{
    public partial class WebView: Form
    {
        private ChromiumWebBrowser view;

        public WebView(String url, String title, String icon, Int32[] geometry)
        {
            this.Text = title;
            this.Icon = new System.Drawing.Icon(icon);

            if (geometry[0] != -1 && geometry[1] != -1)
            {
                this.Location = new System.Drawing.Point(geometry[0], geometry[1]);
            }

            if (geometry[2] != -1 && geometry[3] != -1)
            {
                this.Size = new System.Drawing.Size(geometry[2], geometry[3]);
            }

            this.view = new ChromiumWebBrowser(url);
            this.view.Dock = DockStyle.Fill;
            this.Controls.Add(this.view);
        }
    }
}
