import logging
import json

class InvalidArn(Exception):
    pass

class Arn:

    def __init__(self, entity_arn, logging_level = logging.INFO):
        """
        This helper class consumes a string and validates that it is a valid
        Amazon Resource Name Entity and related actions
        """

        logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')

        split_arn = entity_arn.split(':')
        logging.debug(split_arn)

        if len(split_arn) != 6:
            # Throw an error if the string and resultant list don't contain
            # the 6 sections colon delimited
            # e.g. arn:aws:iam::123456789012:role/service-role/StatesExecutionRole-us-west-2
            raise InvalidArn("The given arn is invalid: {entity_arn}".format(entity_arn=entity_arn))

        self.full_arn           = entity_arn
        self.entity_name        = ''
        self.entity_type        = ''
        self.path               = ''
        self.assuming_entity    = ''
        self.account_number     = split_arn[4]
        self.region             = split_arn[3]
        self.service            = split_arn[2]
        self.extract_entity(split_arn)

    def extract_entity(self, split_arn):
        entity              = split_arn[5].split('/')

        logging.debug('Entity:')
        logging.debug(entity)

        if entity[0] == 'role' or entity[0] == 'policy':
            logging.debug("this entity is a {entity}".format(entity=entity[0]))
            self.entity_type    = entity[0]
            self.entity_name    = entity[len(entity)-1]
            self.path           = '' if entity[len(entity)-1]==entity[1] else entity[1]
            logging.debug('Path:')
            logging.debug(self.path)

        elif entity[0] =='assumed-role':
                logging.debug("this entity is an assumed-role")
                self.entity_type    = entity[0]
                logging.debug(self.entity_type)
                self.entity_name    = entity[1]
                logging.debug(self.entity_name)
                self.assuming_entity = entity[2]
                logging.debug(self.assuming_entity)
        else:
            self.entity_type    = entity[0]
            self.entity_name    = entity[1]

    def is_role(self):
        if self.entity_type == 'role' or self.entity_type == 'assumed-role':
            return True
        return False

    def is_user(self):
        if self.entity_type == 'user':
            return True
        return False

    def is_policy(self):
        if self.entity_type == 'policy':
            return True
        return False

    def is_assumed_role(self):
        if self.entity_type == 'assumed-role' and self.service == 'sts':
            return True
        return False

    def convert_assumed_role_to_role(self):
        if not self.is_assumed_role():
            logging.debug('ARN is not assumed-role. No action taken')
            return
        self.full_arn = self.full_arn.replace(':sts:', ':iam:')
        self.full_arn = self.full_arn.replace(':assumed-role/',':role/')
        self.full_arn = self.full_arn.replace('/'+self.assuming_entity, '')
        logging.info(self.full_arn)

        logging.info('assumed-role converted to role')


    def __rebuild_full_arn__(self):
        pass

    def get_full_arn(self):
        return self.full_arn

    def get_entity_type(self):
        return self.entity_type

    def get_entity_name(self):
        return self.entity_name

    def get_path(self):
        return self.path

    def get_region(self):
        return self.region

    def get_service(self):
        return self.service

    def get_account_number(self):
        return self.account_number
