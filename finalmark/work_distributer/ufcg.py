from utils.work_distributer.requester import RefreshRequester
from utils.work_distributer import Worker

class UfcgDistributer(object):

    def __init__(self, data):
        self.data = data
        self.requester = RefreshRequester('worker_queue')

    def get_marks_from_subjects(self):

        def f(requester, data, subject):
            response = requester.block_request(data)
            subject['marks'] = response['data']

        threads = []
        for subject in self.data.get('subjects'):
            request = {
                "plugin": "finalmark",
                "action": "get_marks_from_subject",
                "username": self.data.get('username'),
                "password": self.data.get('password'),
                "code": subject.get('code'),
                "class": subject.get('class'),
                "subject": {
                    "name": subject.get('name'),
                    "code": subject.get('code'),
                    "class": subject.get('class'),
                    "semester": subject.get('semester')
                },
                "cookiejar": self.data.get('cookiejar')
            }
            worker = Worker(f, self.requester, request, subject)
            worker.start()
            threads.append(worker)

        return threads

    def get_absences_from_subjects(self):

        def f(requester, data, subject):
            response = requester.block_request(data)
            subject['absences'] = response['data']

        threads = []
        for subject in self.data.get('subjects'):
            request = {
                "plugin": "finalmark",
                "action": "get_absences_from_subject",
                "username": self.data.get('username'),
                "password": self.data.get('password'),
                "subject": {
                    "name": subject.get('name'),
                    "code": subject.get('code'),
                    "class": subject.get('class'),
                    "semester": subject.get('semester')
                },
                "cookiejar": self.data.get('cookiejar')
            }
            worker = Worker(f, self.requester, request, subject)
            worker.start()
            threads.append(worker)

        return threads

    def get_user_info(self, user_info):

        def f(requester, data, user_info):
            response = requester.block_request(data)
            user_info.update({"user_info": response['data']})

        request = {
            "plugin": "finalmark",
            "action": "get_user_info",
            "username": self.data.get('username'),
            "password": self.data.get('password'),
            "cookiejar": self.data.get('cookiejar')
        }
        worker = Worker(f, self.requester, request, user_info)
        worker.start()

        return [worker]

    def get_credits(self):

        def f(requester, data, user_info):
            response = requester.block_request(data)
            for i in range(len(response['data'])):
                user_info.get('subjects')[i]['credits'] = response['data'][i]

        request = {
            "plugin": "finalmark",
            "action": "get_credits",
            "username": self.data.get('username'),
            "password": self.data.get('password'),
            "subjects": [s['name'] for s in self.data.get('subjects')],
            "cookiejar": self.data.get('cookiejar')
        }


        worker = Worker(f, self.requester, request, self.data)
        worker.start()

        return [worker]


    def distribute(self, user_info):

        threads = []

        threads += self.get_absences_from_subjects()
        threads += self.get_marks_from_subjects()
        threads += self.get_user_info(user_info)
        threads += self.get_credits()
        for t in threads:
            t.join()
        user_info["subjects"] = self.data.get('subjects')
