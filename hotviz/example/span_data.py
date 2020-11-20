tree_data = [
                        {'label': 'MajorClaim',
                        'link': 1,
                        'link_label': '',
                        'text': 'one who studies overseas will gain many skills throughout this '
                                'experience'},
                        {'label': 'MajorClaim',
                        'link': 1,
                        'link_label': '',
                        'text': 'living and studying overseas gives the individual a new perspective '
                                'on the subject that is studied or in general life'},
                        {'label': 'Claim',
                        'link': 1,
                        'link_label': 'For',
                        'text': 'studying at an overseas university gives individuals the '
                                'opportunity to improve social skills by interacting and '
                                'communicating with students from different origins and cultures'},
                        {'label': 'Claim',
                        'link': 1,
                        'link_label': 'For',
                        'text': 'living and studying overseas is an irreplaceable experience when it '
                                'comes to learn standing on your own feet'},
                        {'label': 'Claim',
                        'link': 1,
                        'link_label': 'For',
                        'text': 'one who has studied and lived overseas will become more eligible '
                                'for the job than his/her peers'},
                        {'label': 'Premise',
                        'link': 2,
                        'link_label': 'Supports',
                        'text': 'Compared to the peers studying in the home country, it will be more '
                                'likely for the one who is living overseas to be successful in '
                                'adapting himself/herself into new environments and situations in '
                                'life'},
                        {'label': 'Premise',
                        'link': 3,
                        'link_label': 'Attacks',
                        'text': 'One who is living overseas will of course struggle with loneliness, '
                                'living away from family and friends'},
                        {'label': 'Premise',
                        'link': 6,
                        'link_label': 'Attacks',
                        'text': 'those difficulties will turn into valuable experiences in the '
                                'following steps of life'},
                        {'label': 'Premise',
                        'link': 3,
                        'link_label': 'Supports',
                        'text': 'the one will learn living without depending on anyone else'},
                        {'label': 'Premise',
                        'link': 4,
                        'link_label': 'Supports',
                        'text': 'employers are mostly looking for people who have international and '
                                'language skills'},
                        {'label': 'Premise',
                        'link': 4,
                        'link_label': 'Supports',
                        'text': 'Becoming successful in this study will give the student an edge in '
                                'job market'},
                        {'label': 'Claim',
                        'link': 1,
                        'link_label': 'Against',
                        'text': 'there are many difficulties a student might face when studying and '
                                'living overseas'}
                        ]


span_data = [
                        {
                                "token": "I",
                                "pred": {
                                            "span_id": None,
                                            "label": None,
                                            },
                        },
                        {
                                "token": "think",
                                "pred": {
                                            "span_id": None,
                                            "label": None,
                                            "score":None,

                                            },
                        },
                        {
                                "token": "that",
                                "pred": {
                                            "span_id": None,
                                            "label": None,
                                            "score": None,

                                            },
                                "gold": {
                                            "span_id": "X_1",
                                            "label": "X",
                                        }

                            },
                        {
                                "token": "this",
                                "pred": {
                                            "span_id": "X_1",
                                            "label": "X",
                                            "score": 0.6,
                                            },
                                "gold": {
                                            "span_id": "X_1",
                                            "label": "X",
                                        }
                        },
                        {
                                "token": "is",
                                "pred": {
                                            "span_id": "X_1",
                                            "label": "X",
                                            "score": 0.7,
                                            },
                                "gold": {
                                            "span_id": "X_1",
                                            "label": "X",
                                        }
                        },
                            {
                                "token": "span",
                                "pred": {
                                            "span_id": "X_1",
                                            "label": "X",
                                            "score": 0.8,
                                            },
                                "gold": {
                                            "span_id": "X_1",
                                            "label": "X",
                                        }
                            },
                        {
                                "token": "number",
                                "pred": {
                                            "span_id": "X_1",
                                            "label": "X",
                                            "score": 0.9,
                                            },
                                "gold": {
                                            "span_id": "X_1",
                                            "label": "X",
                                        }
                        },
                        {
                                "token": "one",
                                "pred": {
                                            "span_id": "X_1",
                                            "label": "X",
                                            "score": 0.7,
                                            },
                                "gold": {
                                            "span_id": "X_1",
                                            "label": "X",
                                        }
                            },
                        {
                                "token": "and",
                                "pred": {
                                            "span_id": None,
                                            "label": None,
                                            "score": None,
                                            },
                        },
                            {
                                "token": "then",
                                "pred": {
                                            "span_id": None,
                                            "label": "Z",
                                            "score": 0.3,

                                            },
                            },
                        {
                                "token": "somewhere",
                                "pred": {
                                            "span_id": None,
                                            "label": "Z",
                                            "score": 0.4,

                                            },
                        },
                        {
                                "token": "here",
                                "pred": {
                                            "span_id": "Z_1",
                                            "label": "Z",
                                            "score": 0.8,
                                            },
                                "gold": {
                                            "span_id": "Z_1",
                                            "label": "Z",
                                        }
                            },
                        {
                                "token": "is",
                                "pred": {
                                            "span_id": "Z_1",
                                            "label": "Z",
                                            "score": 0.9,
                                            },
                                "gold": {
                                            "span_id": "Z_1",
                                            "label": "Z",
                                        }
                        },
                        {
                                "token": "span",
                                "pred": {
                                            "span_id": "Z_1",
                                            "label": "Z",
                                            "score": 0.75,
                                            },
                                "gold": {
                                            "span_id": "Z_1",
                                            "label": "Z",
                                        }
                        },
                            {
                                "token": "number",
                                "pred": {
                                            "span_id": "Z_1",
                                            "label": "Z",
                                            "score": 0.85,
                                            },
                                "gold": {
                                            "span_id": "Z_1",
                                            "label": "Z",
                                        }
                            },
                        {
                                "token": "two",
                                "pred": {
                                            "span_id": "Z_1",
                                            "label": "Z",
                                            "score": 0.95,
                                            },
                                "gold": {
                                            "span_id": "Z_1",
                                            "label": "Z",
                                        }
                        },
                        {
                                "token": ".",
                                "pred": {
                                            "span_id": None,
                                            "label": None,
                                            "score": None,
                                            },
                        },
                        {
                                "token": "Lastly,",
                                "pred": {
                                            "span_id": None,
                                            "label": None,
                                            },
                        },
                            {
                                "token": "we",
                                "pred": {
                                            "span_id": "Z_2",
                                            "label": "Z",
                                            "score": 0.6,
                                            },
                        },
                        {
                                "token": "have",
                                "pred": {
                                            "span_id": "Z_2",
                                            "label": "Z",
                                            "score": 0.7,
                                            },
                        },
                        {
                                "token": "span",
                                "pred": {
                                            "span_id": "Z_2",
                                            "label": "Z",
                                            "score": 0.8,
                                            },
                                "gold": {
                                            "span_id": "Z222222_2",
                                            "label": "Z",
                                        }
                        },
                        {
                                "token": "number",
                                "pred": {
                                            "span_id": "Z_3",
                                            "label": "Z",
                                            "score": 0.9,
                                            },
                                "gold": {
                                            "span_id": "Z222222_2",
                                            "label": "Z",
                                        }
                        },
                        {
                                "token": "three",
                                "pred": {
                                            "span_id": "Z_2",
                                            "label": "Z",
                                            "score": 0.8,
                                            },
                                "gold": {
                                            "span_id": "Z222222_2",
                                            "label": "Z",
                                        }
                        },
                        {
                                "token": ".",
                                "pred": {
                                            "span_id": None,
                                            "label": None,
                                            },

                        },
                        ]