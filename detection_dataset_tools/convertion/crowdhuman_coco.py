# input: crowdhuman dataset with coco(json) format annotations
#   1) crowdhuman 原始格式是 odgt，网上有大哥提供了类似于 coco 的 json 格式，但这个 json 不是标准的 coco 格式，所以需要进行转换。
#   2) 非标准的 coco 格式，就是在一个 annotation 中有 `bbox/hbox/fbox` 三个 box，分别代表可视人物结果、头部box结果、全身box结果（包括没看到的）。
#   3) 原始数据包括两个 category_id，1 是建筑物、水中倒影等的人物的box信息，2是普通人物的box信息。
# output: standard coco format annotations
#   1) coco 格式的数据主要分为 categories、imgs、annotations 三个部分
#   2) categories：确定要生成数据集的类别信息，即 bbox/hbox/fbox 分别对应什么类别，每一类的id是多少
#   3) imgs：图片列表应该跟原始结果没有区别，主要就是 id，
#   4) 标签信息：box 的标签信息还挺多，主要包括 id、image_id、iscrowd、ignore，以及自己设置的 category_id，box，area 字段

import json

def crowdhuamn_coco_to_normal_coco(src_json_path, target_json_path, categories_info=[dict(src="hbox", name="head")]):
    src_dict = json.load(open(src_json_path, "r"))
    target_categories = [dict(id=id, name=cat_info["name"]) for id, cat_info in enumerate(categories_info)]
    src_cat_to_cat_id = {cat_info["src"]: id for id, cat_info in enumerate(categories_info)}
    target_annotations = []

    for anno in src_dict['annotations']:
        if anno["category_id"] != 1:
            # 不处理倒影、雕像等信息
            continue
        # 通用 anno 信息
        image_id = anno["image_id"]
        id = anno["id"]
        iscrowd = anno["iscrowd"]
        ignore = anno["ignore"]
        base_dict = dict(id=id,
                         image_id=image_id,
                         iscrowd=iscrowd,
                         ignore=ignore)

        # 根据
        for cur_box_name in src_cat_to_cat_id.keys():
            if cur_box_name in anno:
                base_dict["category_id"] = src_cat_to_cat_id[cur_box_name]
                base_dict["bbox"] = anno[cur_box_name]
                base_dict["area"] = base_dict["bbox"][2] * base_dict["bbox"][3]
                target_annotations.append(base_dict)

    target_json = dict(images=src_dict["images"],
                       annotations=target_annotations,
                       categories=target_categories)

    json.dump(target_json, open(target_json_path, "w"))
