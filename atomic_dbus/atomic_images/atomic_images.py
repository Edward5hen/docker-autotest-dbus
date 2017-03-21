r"""
Summary
---------

Test atomic dbus service

Operational Detail
----------------------

Prerequisites
---------------

"""

from dbus_client import AtomicDBusClient
from autotest.client import utils
from dockertest.subtest import SubSubtest
from dockertest.subtest import SubSubtestCaller
from dockertest.images import DockerImages
from dockertest.images import DockerContainers


DBUS_OBJ = AtomicDBusClient()


class atomic_dbus(SubSubtestCaller):

    config_section = 'atomic_dbus'


class images_list(SubSubtest):

    def initialize(self):
        super(images_list, self).initialize()
        utils.run('sudo docker pull rhel7/rsyslog')

        self.sub_stuff['dbus_rst'] = ''
        self.sub_stuff['host_rst'] = ''

    def run_once(self):
        super(images_list, self).run_once()
        self.sub_stuff['host_rst'] = utils.run(
                'sudo atomic images list')
        self.sub_stuff['dbus_rst'] = DBUS_OBJ.images_list()

    def postprocess(self):
        super(images_list, self).postprocess()
        self.failif_ne(self.sub_stuff['host_rst'].stdout,
                       self.sub_stuff['dbus_rst'],
                       'Dbus failed to list images!')


class images_help(SubSubtest):

    def initialize(self):
        super(images_help, self).initialize()
        self.sub_stuff['img_id'] = utils.run(
                "sudo docker images | sed -n 2p | awk '{print $3}'")

        self.sub_stuff['dbus_rst'] = ''
        self.sub_stuff['host_rst'] = ''

    def run_once(self):
        super(images_help, self).run_once()
        self.sub_stuff['host_rst'] = utils.run(
                'sudo atomic images help %s' % self.sub_stuff['img_id'])
        self.sub_stuff['dbus_rst'] = DBUS_OBJ.images_help(
                self.sub_stuff['img_id'])

    def postprocess(self):
        super(images_help, self).postprocess()
        self.failif_ne(self.sub_stuff['dbus_rst'],
                       self.sub_stuff['host_rst'].stdout,
                       'Dbus failed to help image %s' %
                       self.sub_stuff['img_id'])


class images_prune(SubSubtest):

    def initialize(self):
        super(images_prune, self).initialize()
        utils.run('sudo atomic install rhel7/rsyslog')
        utils.run('sudo atomic run rhel7/rsyslog')
        # Create dangling image
        utils.run('sudo atomic commit rsyslog')

    def run_once(self):
        super(images_prune, self).run_once()
        DBUS_OBJ.images_prune()

    def postprocess(self):
        super(images_prune, self).postprocess()
        imgs_names = DockerImages(self).list_imgs_full_name()
        self.failif_ne(imgs_names, ['rhel7/rsyslog:lastest'],
                       'Dbus failed to prune dangling images')

    def clean_up(self):
        super(images_prune, self).postprocess()
        ctns = DockerContainers(self)
        ctns.clean_all(['rsyslog'])


class images_info(SubSubtest):

    def initialize(self):
        super(images_info, self).initialize()
        self.sub_stuff['img_info_dbus_rst'] = None
        self.sub_stuff['img_info_host_rst'] = None
        self.sub_stuff['img_info_remote_dbus_rst'] = None
        self.sub_stuff['img_info_remote_host_rst'] = None

    def run_once(self):
        super(images_info, self).run_once()
        self.sub_stuff['img_info_dbus_rst'] = \
            DBUS_OBJ.images_info("rehl7/rsyslog", False)
        self.sub_stuff['img_info_host_rst'] = \
            utils.run('sudo atomic images info rhel7/rsyslog')

        self.sub_stuff['img_info_remote_dbus_rst'] = \
            DBUS_OBJ.images_info('rhel7/sadc', True)
        self.sub_stuff['img_info_remote_host_rst'] = \
            utils.run('sudo atomic images info --remote rhel7/sadc')

    def postprocess(self):
        super(images_info, self).postprocess()
        self.failif_ne(self.sub_stuff['img_info_dbus_rst'],
                       self.sub_stuff['img_info_host_rst'].stdout,
                       'Dbus failed to list rsyslog info')
        self.failif_ne(self.sub_stuff['img_info_remote_dbus_rst'],
                       self.sub_stuff['img_info_remote_host_rst'].stdout,
                       'Dbus failed to list sadc info remotely')


class images_delete(SubSubtest):

    def run_once(self):
        super(images_delete, self).run_once()
        DBUS_OBJ.images_delete('rhel7/rsyslog', False, False)

    def postprocess(self):
        super(images_delete, self).postprocess()
        imgs_names = DockerImages(self).list_imgs_full_name()
        self.failif('rhel7/rsyslog:lastest' in imgs_names,
                    'dbus can not delete image rhel7/rsyslog')


class images_delete_force(SubSubtest):

    def initialize(self):
        super(images_delete_force, self).initialize()
        utils.run('sudo docker pull rhel7/rsyslog')
        utils.run('sudo atomic install rhel7/rsyslog')
        utils.run('sudo atomic run rhel7/rsyslog')

    def run_once(self):
        super(images_delete_force, self).run_once()
        DBUS_OBJ.images_delete('rhel7/rsyslog', True, False)

    def postprocess(self):
        super(images_delete_force, self).postprocess()
        imgs_names = DockerImages(self).list_imgs_full_name()
        self.failif('rhel7/rsyslog:lastest' in imgs_names,
                    'dbus can not delete image rhel7/rsyslog forcely')
