#!/usr/bin/env python2
import uuid
from captcha.image import ImageCaptcha


class Captcha(object):
    def __init__(self, img_path, font):
        self.img_path = img_path
        self.font = font


    def gen_captcha(self):
        """
        :param path_img:
        :param font:
        :return:
        """
        self.captcha = str(uuid.uuid1())[:5]
        self.image = ImageCaptcha(fonts=[self.font, self.font])
        self.image.generate(self.captcha)
        self.image.write(self.captcha, '{1}/{2}.png'.format(self.img_path, self.captcha))
        return '{0}/{1}.png'.format(self.img_path, self.captcha)


if __name__ == '__main__':
    print Captcha('/tmp/', '/usr/share/fonts/dejavu/DejaVuSansMono.ttf').gen_captcha()
