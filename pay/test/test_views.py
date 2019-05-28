import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestSigup(unittest.TestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        capabilities = options.to_capabilities()
        self.driver = webdriver.Chrome(desired_capabilities=capabilities, port=2525)

    def test_get_index(self):
        self.driver.get("http://192.168.100.142:8000/")
        title = self.driver.title
        self.assertEqual('Net Provider Solutions LLC',title)
        print(self.driver.title)
        self.driver.close()

    def test_sign_up(self):
        self.driver.get("http://192.168.100.142:8000/")
        self.driver.implicitly_wait(30)
        username = self.driver.find_element_by_name('username')
        password = self.driver.find_element_by_name('password')
        username.clear()
        password.clear()
        username.send_keys('admin')
        password.send_keys('123456')
        password.submit()
        self.driver.implicitly_wait(30)
        cdrs = self.driver.find_element_by_tag_name('h2').text
        self.assertEqual('Cdrs',cdrs)
        self.driver.close()


    def test_sign_error(self):
        self.driver.get("http://192.168.100.142:8000/")
        self.driver.implicitly_wait(30)
        username = self.driver.find_element_by_name('username')
        password = self.driver.find_element_by_name('password')
        username.clear()
        password.clear()
        username.send_keys('admin')
        password.send_keys('1234')
        password.submit()


