package com.sei.server;

import com.sei.agent.Device;
import com.sei.bean.View.ViewTree;
import com.sei.server.component.Handler;
import com.sei.server.component.Scheduler;
import com.sei.util.*;
import com.sei.util.client.ClientAdaptor;
import fi.iki.elonen.NanoHTTPD;
import fi.iki.elonen.util.ServerRunner;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.util.*;

import static com.sei.util.CommonUtil.DEFAULT_PORT;
import static com.sei.util.CommonUtil.log;

public class Control extends NanoHTTPD{
    public static HashMap<String, Handler> route_table = new HashMap<>();
    public static Scheduler scheduler;
    JSONObject config_json;
    //List<Device> devices = new ArrayList<>();
    Map<String, Device> devices = new HashMap<>();


    public static void main(String[] argv) {
        setListeningPort();
        Control server = new Control();
        server.set_route_table();
        server.configure(argv);
        System.out.println("listening on: " + DEFAULT_PORT);
        // WebviewService webviewService = new WebviewService();
        // webviewService.start();
        ServerRunner.run(Control.class);
    }

    public Control(){
        super(CommonUtil.DEFAULT_PORT);
    }

    public void register(String route, Handler handler){
        route_table.put(route, handler);
    }
    public void set_route_table(){
        register("/", new Handler() {
            @Override
            public Response onRequest(IHTTPSession session) {
                return newFixedLengthResponse("hello!!!");
            }
        });


        register("/list", new Handler() {
            @Override
            public Response onRequest(IHTTPSession session) {
                JSONObject jo = new JSONObject();
                try {
                    jo.put("nodes", scheduler.graphAdjustor.getAllNodesTag());
                    jo.put("activity", scheduler.graphAdjustor.getAllNodesTag().size());
                }catch (Exception e){
                    e.printStackTrace();
                }
                return newFixedLengthResponse(jo.toString());
            }
        });

        register("/replay", new Handler() {
            @Override
            public Response onRequest(IHTTPSession session) {
                // parameter format : /replay?serial=xxx&nodes=xxx_xxx&xxx_xxx

                String query = session.getQueryParameterString().substring(7);
                String serial = Arrays.asList(query.split("&")).get(0);
                if (devices.containsKey(serial)){
                    return newFixedLengthResponse(serial + " still running");
                }

                //log(query.toString());
                if (query.equals("all")) {
                    //strategy = new ModelReplay(graphManager);
                    //strategy.start();
                }else{
                    try {
                        List<String> route_list = Arrays.asList(query.split("&"));
                        JSONArray device_config = config_json.getJSONArray("DEVICES");
                        for (int i = 0; i < device_config.length(); i++) {
                            JSONObject c = device_config.getJSONObject(i);
                            if (!c.getString("SERIAL").equals(serial))
                                continue;
                            String pkg = config_json.getString("PACKAGE");
                            String ip = "http://" + c.getString("IP");
                            String pass = "";
                            if (c.has("PASSWORD")) pass = c.getString("PASSWORD");
                            if (ip.contains("127.0.0.1"))
                                ShellUtils2.execCommand("adb -s " + serial + " forward tcp:" + c.getInt("PORT") + " tcp:6161");
                            Device d = new Device(ip, c.getInt("PORT"), serial, pkg, pass, 0);
                            d.setRoute_list(route_list);
                            scheduler.bind(d);
                            d.start();
                            break;
                        }
                    }catch (Exception e){
                        e.printStackTrace();
                    }
                    //strategy = new ModelReplay(graphManager, route_list);
                    //strategy.start();
                }
                return newFixedLengthResponse("replay start");
            }
        });

        register("/save", new Handler() {
            @Override
            public Response onRequest(IHTTPSession session) {
                log("save graph");
                scheduler.graphAdjustor.save();
                scheduler.save();
                return newFixedLengthResponse("save");
            }
        });

        register("/stop", new Handler() {
            @Override
            public Response onRequest(IHTTPSession session) {
                // parameter format : /stop?serial=xxx
                String query = session.getQueryParameterString().substring(7);
                log("stop device: " + query);
                if(devices.containsKey(query)){
                    devices.get(query).Exit = true;
                    devices.remove(query);
                }
                return newFixedLengthResponse("stop");
            }
        });

        register("/finish", new Handler() {
            @Override
            public Response onRequest(IHTTPSession session) {
                // format: /print?serial=xxx
                String query = session.getQueryParameterString().substring(7);
                log("print device: " + query);
                if(devices.containsKey(query)){
                    ViewTree tempTree = devices.get(query).currentTree;
                }
                return newFixedLengthResponse("print device: " + query);
            }
        });

        register("/print", new Handler() {
            @Override
            public Response onRequest(IHTTPSession session) {
                // format: /finish?serial=xxx
                String query = session.getQueryParameterString().substring(7);
                for (String key: devices.keySet()){
                    Device d = devices.get(key);
                    if (d.serial.equals(query)){
                        if (d.Exit) return newFixedLengthResponse("yes");
                        else return newFixedLengthResponse("no");
                    }
                }

                return newFixedLengthResponse("unknown serial");
            }
        });
    }

    @Override
    public Response serve(IHTTPSession session){
        String url = session.getUri();
        Handler handler = route_table.get(url);
        if (handler == null)
            return newFixedLengthResponse("unknown command");
        else {
            return handler.onRequest(session);
        }
    }

    public static void setListeningPort(){
        try {
            //String dir = "/home/mike/togithub/droidwalker/droidwalker/out/artifacts/droidwalker_jar/";
            String dir = "./";
            File config = new File(dir + "config.json");
            if (!config.exists()) return;
            String content = CommonUtil.readFromFile(dir + "config.json");
            JSONObject config_json = new JSONObject(content);
            CommonUtil.DEFAULT_PORT = config_json.getInt("DEFAULT_PORT");
        }catch(Exception e){
            e.printStackTrace();
        }

    }

    void configure(String[] argv){
        String dir = "./";
        File config = new File(dir + "config.json");
        if (!config.exists()) return;
        try {
            String content = CommonUtil.readFromFile(dir + "config.json");
            config_json = new JSONObject(content);
            if (config_json.has("ADB_PATH")){
                log("ADB: " + config_json.getString("ADB_PATH"));
                CommonUtil.ADB_PATH = config_json.getString("ADB_PATH");
            }

            if (config_json.has("BACKEND")){
                String backEnd = config_json.getString("BACKEND");
                log("Backend: " + backEnd);

                if (backEnd.contains("UIAutomator")){
                    ClientAdaptor.type = 0;
                }else if (backEnd.contains("Xposed")){
                    ClientAdaptor.type = 1;
                }else{
                    log("unsupported backend: " + backEnd + " default UIAutomator");
                }
            }

            /*if (config_json.has("TARGET_ACTIVITY")){
                String target = config_json.getString("TARGET_ACTIVITY");
                log("Target："+ target);
            }*/

            String pkg = config_json.getString("PACKAGE");
            ConnectUtil.setUp(pkg);
            JSONArray device_config = config_json.getJSONArray("DEVICES");

            if (argv.length > 0) {
                scheduler = new Scheduler(argv[0], devices);
                if (argv[0].contains("-p")) return;
            }else
                scheduler = new Scheduler("", devices);

            for(int i=0; i < device_config.length(); i++){
                JSONObject c = device_config.getJSONObject(i);
                String serial = c.getString("SERIAL");
                if (!ClientUtil.connected(serial)){
                    log(serial + " not connected");
                    continue;
                }

                String ip = "http://" + c.getString("IP");

                String pass = "";
                if (c.has("PASSWORD")) pass = c.getString("PASSWORD");

                if (ip.contains("127.0.0.1"))
                    ShellUtils2.execCommand("adb -s " + serial + " forward tcp:" + c.getInt("PORT") + " tcp:6161");

                Device d;
                if (argv.length >0 && argv[0].contains("-s")){
                    d = new Device(ip, c.getInt("PORT"), serial, pkg, pass, 3);     //爬虫模式
                    CommonUtil.SCREENSHORT = false;         //不截取其他页面
                    if (config_json.has("TARGET_ACTIVITY")) {
                        String target = config_json.getString("TARGET_ACTIVITY");
                        d.setTargetActivity(target);
                        log("Target：" + target);
                    } else {
                        log("error：no target!");
                    }
                }else if (argv.length >0 && argv[0].contains("-r")){
                    d = new Device(ip, c.getInt("PORT"), serial, pkg, pass, 2);
                }else{
                    d = new Device(ip, c.getInt("PORT"), serial, pkg, pass, 1);
                }

                scheduler.bind(d);
            }


            for (String key: devices.keySet()){
                devices.get(key).start();
            }


        }catch (Exception e){
            e.printStackTrace();
        }
    }
}
