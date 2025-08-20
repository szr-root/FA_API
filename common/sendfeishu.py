# coding=utf-8
"""
    @project: FA_API
    @file： send_feishu.py
    @Author：John
    @date：2025/8/9 13:53
"""
import datetime

from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

app_id = os.getenv('APP_ID')
app_secret = os.getenv('APP_SECRET')
feishu_url = os.getenv('FEISHU_URL')


def get_tenant_access_key():
    url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal'
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    res = requests.post(url, data=data)
    return res.json().get('tenant_access_token')


def feishu_send_message(result, id, info,
                            url=feishu_url):
    object_list_1 = result['results']

    # print(object_list_1)

    headers = {"Content-Type": "application/json"}
    payload_message = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "i18n_elements": {
                "zh_cn": [
                    # {
                    #     "tag": "markdown",
                    #     "content": "**数据总览** ",
                    #     "text_align": "left",
                    #     "text_size": "heading"
                    # },
                    {
                        "tag": "markdown",
                        "content": f":OnIt:**任务名**: {info['task']}",
                        "text_align": "left",
                        "text_size": "heading"
                    },

                    {
                        "tag": "markdown",
                        "content": f":VRHeadset:**执行环境**: {info['env']}",
                        "text_align": "left",
                        "text_size": "heading"
                    },

                    {
                        "tag": "column_set",
                        "flex_mode": "bisect",
                        "background_style": "default",
                        "horizontal_spacing": "8px",
                        "horizontal_align": "center",
                        "columns": [
                            {
                                "tag": "column",
                                "width": "weighted",
                                "vertical_align": "top",
                                "vertical_spacing": "8px",
                                "background_style": "default",
                                "elements": [
                                    {
                                        "tag": "column_set",
                                        "flex_mode": "none",
                                        "background_style": "default",
                                        "horizontal_spacing": "8px",
                                        "horizontal_align": "left",
                                        "columns": [
                                            {
                                                "tag": "column",
                                                "width": "weighted",
                                                "vertical_align": "top",
                                                "vertical_spacing": "8px",
                                                "background_style": "grey",
                                                "elements": [
                                                    {
                                                        "tag": "markdown",
                                                        "content": ":DONE:总用例数",
                                                        "text_align": "center",
                                                        "text_size": "normal"
                                                    },
                                                    {
                                                        "tag": "column_set",
                                                        "flex_mode": "none",
                                                        "horizontal_spacing": "default",
                                                        "background_style": "default",
                                                        "columns": [
                                                            {
                                                                "tag": "column",
                                                                "elements": [
                                                                    {
                                                                        "tag": "div",
                                                                        "text": {
                                                                            "tag": "plain_text",
                                                                            "content": f"{result['all']}",
                                                                            "text_size": "heading",
                                                                            "text_align": "center",
                                                                            "text_color": "default"
                                                                        }
                                                                    }
                                                                ],
                                                                "width": "weighted",
                                                                "weight": 1
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        "tag": "markdown",
                                                        "content": "<text_tag color='blue'>总共100%</text_tag>",
                                                        "text_align": "center",
                                                        "text_size": "normal"
                                                    }
                                                ],
                                                "weight": 1
                                            }
                                        ],
                                        "margin": "0px 0px 0px 0px"
                                    }
                                ],
                                "weight": 1
                            },
                            {
                                "tag": "column",
                                "width": "weighted",
                                "vertical_align": "top",
                                "vertical_spacing": "8px",
                                "background_style": "default",
                                "elements": [
                                    {
                                        "tag": "column_set",
                                        "flex_mode": "none",
                                        "background_style": "default",
                                        "horizontal_spacing": "8px",
                                        "horizontal_align": "left",
                                        "columns": [
                                            {
                                                "tag": "column",
                                                "width": "weighted",
                                                "vertical_align": "top",
                                                "vertical_spacing": "8px",
                                                "background_style": "grey",
                                                "elements": [
                                                    {
                                                        "tag": "markdown",
                                                        "content": ":PRAISE:成功用例数",
                                                        "text_align": "center",
                                                        "text_size": "normal"
                                                    },
                                                    {
                                                        "tag": "column_set",
                                                        "flex_mode": "none",
                                                        "horizontal_spacing": "default",
                                                        "background_style": "default",
                                                        "columns": [
                                                            {
                                                                "tag": "column",
                                                                "elements": [
                                                                    {
                                                                        "tag": "div",
                                                                        "text": {
                                                                            "tag": "plain_text",
                                                                            "content": f"{result['success']}",
                                                                            "text_size": "heading",
                                                                            "text_align": "center",
                                                                            "text_color": "green"
                                                                        }
                                                                    }
                                                                ],
                                                                "width": "weighted",
                                                                "weight": 1
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        "tag": "markdown",
                                                        "content": f"<text_tag color='green'>成功率{format(result['success'] / result['all'] * 100, '.2f')}%</text_tag>",
                                                        "text_align": "center",
                                                        "text_size": "normal"
                                                    }
                                                ],
                                                "weight": 1
                                            }
                                        ],
                                        "margin": "0px 0px 0px 0px"
                                    }
                                ],
                                "weight": 1
                            },
                            {
                                "tag": "column",
                                "width": "weighted",
                                "vertical_align": "top",
                                "vertical_spacing": "8px",
                                "background_style": "default",
                                "elements": [
                                    {
                                        "tag": "column_set",
                                        "flex_mode": "none",
                                        "background_style": "default",
                                        "horizontal_spacing": "8px",
                                        "horizontal_align": "left",
                                        "columns": [
                                            {
                                                "tag": "column",
                                                "width": "weighted",
                                                "vertical_align": "top",
                                                "vertical_spacing": "8px",
                                                "background_style": "grey",
                                                "elements": [
                                                    {
                                                        "tag": "markdown",
                                                        "content": ":SHOCKED:失败用例数",
                                                        "text_align": "center",
                                                        "text_size": "normal"
                                                    },
                                                    {
                                                        "tag": "column_set",
                                                        "flex_mode": "none",
                                                        "horizontal_spacing": "default",
                                                        "background_style": "default",
                                                        "columns": [
                                                            {
                                                                "tag": "column",
                                                                "elements": [
                                                                    {
                                                                        "tag": "div",
                                                                        "text": {
                                                                            "tag": "plain_text",
                                                                            "content": f"{result['fail'] + result['error']}",
                                                                            "text_size": "heading",
                                                                            "text_align": "center",
                                                                            "text_color": "red"
                                                                        }
                                                                    }
                                                                ],
                                                                "width": "weighted",
                                                                "weight": 1
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        "tag": "markdown",
                                                        "content": f"<text_tag color='red'>失败率{format((result['fail'] + result['error']) / result['all'] * 100, '.2f')}%</text_tag>",
                                                        "text_align": "center",
                                                        "text_size": "normal"
                                                    }
                                                ],
                                                "weight": 1
                                            }
                                        ],
                                        "margin": "0px 0px 0px 0px"
                                    }
                                ],
                                "weight": 1
                            }
                        ],
                        "margin": "16px 0px 0px 0px"
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "column_set",
                        "flex_mode": "none",
                        "background_style": "default",
                        "horizontal_spacing": "8px",
                        "horizontal_align": "left",
                        "columns": [
                            {
                                "tag": "column",
                                "width": "weighted",
                                "vertical_align": "center",
                                "vertical_spacing": "8px",
                                "background_style": "default",
                                "elements": [
                                    {
                                        "tag": "markdown",
                                        "content": "**本次运行测试场景**",
                                        "text_align": "left",
                                        "text_size": "normal"
                                    }
                                ],
                                "weight": 1
                            }
                        ],
                        "margin": "16px 0px 0px 0px"
                    },

                ]
            },
            "i18n_header": {
                "zh_cn": {
                    "title": {
                        "tag": "plain_text",
                        "content": "接口测试任务报告"
                    },
                    "subtitle": {
                        "tag": "plain_text",
                        "content": f"时间：{str(datetime.datetime.now().strftime('%Y-%m-%d'))}"
                    },
                    "template": "blue",
                    "ud_icon": {
                        "tag": "standard_icon",
                        "token": "approval_colorful"
                    }
                }
            }},
    }
    for data in object_list_1:
        payload_message['card']['i18n_elements']['zh_cn'].append(
            {
                "tag": "column_set",
                "flex_mode": "none",
                "background_style": "default",
                "horizontal_spacing": "8px",
                "horizontal_align": "left",
                "columns": [
                    {
                        "tag": "column",
                        "width": "weighted",
                        "vertical_align": "center",
                        "vertical_spacing": "8px",
                        "background_style": "default",
                        "elements": [{
                            "tag": "markdown",
                            "content": f"{data['name']}",
                            "text_align": "center",
                            "text_size": "normal"
                        },
                            {
                                "tag": "column_set",
                                "flex_mode": "none",
                                "background_style": "default",
                                "horizontal_spacing": "8px",
                                "horizontal_align": "left",
                                "columns": [
                                    {
                                        "tag": "column",
                                        "width": "weighted",
                                        "vertical_align": "top",
                                        "vertical_spacing": "4px",
                                        "background_style": "grey",
                                        "elements": [
                                            {
                                                "tag": "markdown",
                                                "content": f"该场景总用例数\n{data['all']}",
                                                "text_align": "center",
                                                "text_size": "notation"
                                            }
                                        ],
                                        "weight": 1,
                                        "padding": "0px 0px 12px 0px"
                                    },
                                    {
                                        "tag": "column",
                                        "width": "weighted",
                                        "vertical_align": "top",
                                        "background_style": "grey",
                                        "elements": [
                                            {
                                                "tag": "markdown",
                                                "content": f"该流程下执行成功用例数\n{data['success']}",
                                                "text_align": "center",
                                                "text_size": "notation"
                                            }
                                        ],
                                        "weight": 1
                                    },
                                    {
                                        "tag": "column",
                                        "width": "weighted",
                                        "vertical_align": "top",
                                        "background_style": "grey",
                                        "elements": [
                                            {
                                                "tag": "markdown",
                                                "content": f"执行失败用例数\n{data['fail'] + data['error']}",
                                                "text_align": "center",
                                                "text_size": "notation"
                                            }
                                        ],
                                        "weight": 1
                                    }
                                ],
                                "margin": "16px 0px 0px 0px"
                            }],

                        "weight": 1,
                        "padding": "0px 0px 0px 0px"
                    }
                ],
                "margin": "16px 0px 4px 0px"
            }
        )

    payload_message['card']['i18n_elements']['zh_cn'].append(
        {
            "tag": "hr"
        }
    )
    payload_message['card']['i18n_elements']['zh_cn'].append(
        {
            "elements": [
                {
                    "content": f"[详细用例执行情况请网页查看](http://172.20.20.54:8080/#/records/report/{id})",
                    "tag": "lark_md"
                }
            ],
            "tag": "note"
        }
    )

    res = requests.post(url=url, headers=headers, data=json.dumps(payload_message), )

    print(res.json())
    return res.json()


if __name__ == '__main__':
    pass
    # tenant_access_token = get_tenant_access_key()

    # user_token = 'u-cqIm1x7KhcLUt0KsyPzcyYk03keQ4kNbOMw0lkyE00ma'
    # 个人测试
    # url = "https://open.feishu.cn/open-apis/bot/v2/hook/548cccf2-2fa1-4c8e-a31f-f135b8e562c7"
    # 测试组群聊
    # url = "https://open.feishu.cn/open-apis/bot/v2/hook/46654635-7e10-4235-8ccb-5e945eca2177"

    # 大群群聊
    # url = "https://open.feishu.cn/open-apis/bot/v2/hook/cbc3f551-2292-4e04-a1bd-8ae608176263"

    # done, doing, wait = get_messages(tenant_access_token)

    # new_feishu_send_massage(result)
