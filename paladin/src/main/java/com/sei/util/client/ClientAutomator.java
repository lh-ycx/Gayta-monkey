package com.sei.util.client;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.sei.agent.Device;
import com.sei.bean.View.Action;
import com.sei.bean.View.ViewNode;
import com.sei.bean.View.ViewTree;
import com.sei.util.*;

import java.util.List;


public class ClientAutomator {

    public static void main(String[] argv){
        //Device d = new Device("http://127.0.0.1", 6161, "192.168.59.101:5555", "com.tencent.mm", "monkeymonkey");
        try{
            //init(d);
            //getCurrentTree(d);
            String x = "abc";
            System.out.println(x.equals(null));
        }catch (Exception e){
            e.printStackTrace();
        }
    }
    public static void init(Device d) throws Exception{
        String command = CommonUtil.ADB_PATH + "adb -s " + d.serial + " shell uiautomator runtest" +
                " bundle.jar uiautomator-stub.jar -c com.github.uiautomatorstub.Stub";
        Process p = Runtime.getRuntime().exec(command);
        CommonUtil.sleep(2000);
        String command2 = CommonUtil.ADB_PATH + "adb -s " + d.serial + " forward tcp:" + d.port + " tcp:9008";
        ShellUtils2.execCommand(command2);
    }



    public static ViewTree getCurrentTree(Device d){
        JSONObject data = new JSONObject();
        data.put("jsonrpc", "2.0");
        data.put("method", "dumpWindowHierarchy");
        data.put("id", 1);
        JSONArray params = new JSONArray();
        params.add(false);
        params.add("view.xml");
        data.put("params", params);

        String route = d.ip + ":" + d.port + "/jsonrpc/0";
        try {
            String response = ConnectUtil.postJson(route, data);
            if (response.contains("Success")){
                //d.log(response);
                String xml = "view-" + d.serial + ".xml";
                ShellUtils2.execCommand(CommonUtil.ADB_PATH + "adb -s " + d.serial  + " pull /data/local/tmp/view.xml " + CommonUtil.DIR + xml);
                ShellUtils2.execCommand(CommonUtil.ADB_PATH + "adb -s " + d.serial + " shell rm /data/local/tmp/view.xml");
                String content = CommonUtil.readFromFile(CommonUtil.DIR + xml);
                ViewTree tree = new ViewTree(d, content);
                //xml = "view-" + tree.getActivityName() + tree.getTreeStructureHash() + ".xml";
                //CommonUtil.writeToFile(xml, content);
                return tree;
            }else{
                d.log(response);
                return null;
            }
        }catch (Exception e){
            e.printStackTrace();
            return null;
        }

    }

    public static int execute_action(Device d, int code, ViewTree tree, String path){
        int[] pxy = new int[2];
        if (code == Action.action_list.CLICK){
            ViewNode vn = parse_path(d, tree, path, pxy);
            if (vn == null) return Device.UI.SAME;

            d.log(vn.getResourceID() + "(" + pxy[0] + "," + pxy[1] + ") " );
            if (pxy[0] > d.screenWidth || pxy[0] < 0)
                return Device.UI.SAME;

            for(int i = 0; i < 6; ++i) {
                if (pxy[1] < 0) {
                    d.log("scroll up " + pxy[1]);
                    ClientAdaptor.scrollUp(d);
                    ViewTree tree1 = getCurrentTree(d);
                    parse_path(d, tree1, path, pxy);
                }else if(pxy[1] > d.screenHeight){
                    d.log("scroll down " + pxy[1]);
                    ClientAdaptor.scrollDown(d);
                    ViewTree tree1 = getCurrentTree(d);
                    parse_path(d, tree1, path, pxy);
                }
            }

            if (pxy[1] < 0 || pxy[1] > d.screenHeight)
                return Device.UI.SAME;
            else{
                ClientAdaptor.click(d, pxy[0], pxy[1]);
            }
        }

        switch (code){
            case Action.action_list.BACK:
                ClientAdaptor.goBack(d);
                break;
            case Action.action_list.MENU:
                ClientAdaptor.clickMenu(d);
                break;
            case Action.action_list.ENTERTEXT:
                ClientAdaptor.enterText(d, path);
        }

        String f = ClientAdaptor.getForeground(d);
        if (!f.contains(ConnectUtil.launch_pkg))
            return Device.UI.OUT;

        CommonUtil.sleep(800);
        ViewTree newTree = getCurrentTree(d);
        if (newTree.root == null) return Device.UI.OUT;

        if (!newTree.getActivityName().equals(d.currentTree.getActivityName()) || newTree.getTreeStructureHash() != d.currentTree.getTreeStructureHash()){
            return Device.UI.NEW;
        }else{
            if(true) { return Device.UI.SAME; }     //待修改
            else { return Device.UI.ALL_SAME; }
        }
    }

    public static ViewNode parse_path(Device d, ViewTree tree, String path, int[] pxy){
        ViewNode vn = ViewUtil.getViewByPath(tree.root, path);
        if (vn == null){
            //CommonUtil.storeTree(tree);
            return vn;
        }
        pxy[0] = vn.getX() + vn.getWidth() / 2;
        pxy[1] = vn.getY() + vn.getHeight() / 2;

        if (pxy[0] > d.screenWidth)
            pxy[0] = (vn.getX() + d.screenWidth) / 2;
        else if (pxy[0] < 0){
            pxy[0] = (pxy[0] + vn.getX() + vn.getWidth()) / 2;
        }

        return vn;
    }

    public static Boolean checkPermission(Device d){
        Boolean checked = false;

        String f = ClientAdaptor.getForeground(d);
        CommonUtil.sleep(2000);
        while (f.contains("packageinstaller")){
            ViewTree tree = getCurrentTree(d);
            if (tree == null || tree.root == null) break;

            List<ViewNode> nodes = tree.fetch_clickable_nodes();
            for(ViewNode node : nodes){
                if (node.getViewTag().contains("Button") &&
                        (node.getViewText().contains("Allow") || node.getViewText().contains("允许"))) {
                    int x = node.getX() + node.getWidth() / 2;
                    int y = node.getY() + node.getHeight() / 2;
                    d.log("Allow permission");
                    checked = true;
                    ClientAdaptor.click(d, x, y);
                    break;
                }
            }
            CommonUtil.sleep(1000);
        }

        f = ClientAdaptor.getForeground(d);
        if (!checked && f.contains("packageinstaller")){
            ClientAdaptor.goBack(d);
        }

        return checked;
    }

}
