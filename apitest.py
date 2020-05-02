import requests
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        pass
    def test_api(self,url,method,headers,data,assertion,token=None,content=None,before=None,after=None,):

        self.headers = headers
        self.data = data
        assertion = int(assertion)


        if method == 'post' or 'POST':
            r = requests.post(url,headers=self.headers,data=self.data,)
            try:
                a = self.assertEqual(r.status_code, assertion)
                return True
            except:
                return False
        else:
            r = requests.get(url,headers=headers,)

            try:
                a = self.assertEqual(r.status_code, assertion)
                return True
            except:
                #return print(assertion)
                return False
    def tearDown(self):

        pass


if __name__ == '__main__':
    pass
