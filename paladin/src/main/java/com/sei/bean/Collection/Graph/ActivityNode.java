package com.sei.bean.Collection.Graph;

import com.sei.bean.View.ViewTree;
import com.sei.util.CommonUtil;

import java.util.ArrayList;
import java.util.List;

import static com.sei.util.CommonUtil.log;

/**
 * Created by vector on 16/6/20.
 */
public class ActivityNode {
    String activity_name;
    List<FragmentNode> fragments;
    String ser_intent;

    public ActivityNode(){
        fragments = new ArrayList<>();
    }
    public ActivityNode(String act){this(); activity_name = act;}

    public String getSer_intent() {
        return ser_intent;
    }

    public void setSer_intent(String ser_ntent) {
        this.ser_intent = ser_ntent;
    }

    public FragmentNode find_Fragment(int hash, List<String> click_lists){
        for (FragmentNode vc : fragments){
            if(vc.getStructure_hash() == hash)
                return vc;
        }

        for (FragmentNode vc : fragments){
            float match = 0f;
            for (String s : click_lists){
                if (vc.get_Clickable_list().contains(s))
                    match += 1;
            }

            int tot = vc.get_Clickable_list().size() + click_lists.size();
            if (2 * match / tot > CommonUtil.SIMILARITY){
                FragmentNode fc = new FragmentNode();
                fc.set_Clickable_list(click_lists);
                fc.setStructure_hash(hash);
                fc.setActivity(vc.getActivity());
                fc.interpaths = vc.interpaths;
                fc.intrapaths = vc.intrapaths;
                fc.menuClicked = vc.menuClicked;
                fragments.add(fc);
                return fc;
            }
        }
        return null;
    }

    public FragmentNode find_Fragment(ViewTree vt){
        for (FragmentNode vc : fragments){
            if(vc.getStructure_hash() == vt.getTreeStructureHash())
                return vc;
        }

        for (FragmentNode vc : fragments){
            float match = 0f;
            for (String s : vt.getClickable_list()){
                if (vc.get_Clickable_list().contains(s))
                    match += 1;
            }

            int tot = vc.get_Clickable_list().size() + vt.getClickable_list().size();
            if (2 * match / tot > CommonUtil.SIMILARITY){
                FragmentNode fc = new FragmentNode(vt);
                //深拷贝点击过的节点
                for(int i : vc.path_index) {
                    String path = vc.path_list.get(i);
                    if (fc.path_list.contains(path)){
                        int idx = fc.path_list.indexOf(path);
                        fc.path_index.add(idx);
                    }
                }

                fc.interpaths = vc.interpaths;
                fc.intrapaths = vc.intrapaths;
                fc.menuClicked = vc.menuClicked;
                //fragments.add(fc);
                return fc;
            }
        }
        return null;
    }

    public FragmentNode find_Fragment_in_graph(ViewTree vt){
        for (FragmentNode vc : fragments){
            if (vc.getStructure_hash() == vt.getTreeStructureHash()) {
                return vc;
            }
        }

        for (FragmentNode vc : fragments){
            float match = 0f;
            for (String s : vc.get_Clickable_list()){
                if (vt.getClickable_list().contains(s)) {
//                    Log.i("liuyi", s);
                    match += 1;
                }
            }
            int tot = (vc.get_Clickable_list().size() + vt.getClickable_list().size());
            log(vc.getStructure_hash() + " match : " + 2 * match + " size: " + tot + " rate: " + 2 * match / tot);
            if (2 * match / tot >= 0.85){
//                FragmentNode fc = new FragmentNode(vt.treeStructureHash, vt);
                return vc;
            }
        }
        return null;
    }

    public FragmentNode find_Fragment_in_graph_beta(ViewTree vt){
        log("tree: " + vt.getTreeStructureHash());

        for (FragmentNode vc : fragments){
            if (vc.getStructure_hash() == vt.getTreeStructureHash()) {
                return vc;
            }
        }

        for (FragmentNode vc : fragments){
            log("fragment: " + vc.getStructure_hash());

            float match = calculate_similarity(vc.get_Clickable_list(), vt.getClickable_list());
            log("match: " + match);
            if (match > CommonUtil.SIMILARITY)
                return vc;
        }

        return null;
    }


    private float calculate_similarity(List<String> clickable_list1, List<String> clickable_list2){
        float match = 0f;
        for (String s1 : clickable_list1){
            String[] slist1 = s1.split("/");
            for (String s2 : clickable_list2){
                float xmatch = 0f;
                String[] slist2 = s2.split("/");
                if (!slist1[slist1.length-1].equals(slist2[slist2.length-1]))
                    continue;

                //log(s1 + " vs:\n" + s2);
                for (int a=slist1.length-1, b=slist2.length-1; a >=0 && b >=0;){
                    if (slist1[a].equals(slist2[b])) {
                        xmatch++;
                        --a;
                        --b;
                    }else if (slist1.length < slist2.length)
                        --b;
                    else
                        --a;
                }
                float rate = 2 * xmatch / (slist1.length + slist2.length);


                if (rate > 0.7) {
                    match += 1;
                    break;
                }
            }
        }
        int tot = (clickable_list1.size() + clickable_list2.size());
        return 2 * match / tot;
    }

    public String getActivity_name() {
        return activity_name;
    }

    public void setActivity_name(String activity_name) {
        this.activity_name = activity_name;
    }

    public List<FragmentNode> getFragments() {
        return fragments;
    }

    public void setFragments(List<FragmentNode> fragments) {
        this.fragments = fragments;
    }

    public FragmentNode getFragment(int hash){
        for (FragmentNode vc: fragments)
            if (vc.structure_hash == hash)
                return vc;
        return null;
    }

    public void appendFragment(FragmentNode node){
        fragments.add(node);
    }
}
