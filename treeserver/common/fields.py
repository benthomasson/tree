from django.db import models
import json
import uuid
from django.core import serializers

from south.modelsinspector import add_introspection_rules


class JSONValueField(models.TextField):
    """JSONDictField is a generic textfield that neatly serializes/unserializes
JSON objects seamlessly"""

    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""
        try:
            if isinstance(value, basestring):
                return json.loads(value)
            else:
                return value
        except ValueError, e:
            return value

    def get_db_prep_save(self, value, *args, **kwargs):
        """Convert our JSON object to a string before we save"""
        value = json.dumps(value)
        return super(JSONValueField, self).get_db_prep_save(value, *args, **kwargs)

add_introspection_rules([], ["^common\.fields\.JSONValueField"])


class JSONDictField(models.TextField):
    """JSONDictField is a generic textfield that neatly serializes/unserializes
JSON objects seamlessly"""

    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""

        if value == "":
            return {}

        try:
            if isinstance(value, basestring):
                return json.loads(value)
            elif isinstance(value,dict):
                return value
            else:
                return {}
        except ValueError:
            return {}

    def get_db_prep_save(self, value, *args, **kwargs):
        """Convert our JSON object to a string before we save"""

        if value == "":
            return None

        if isinstance(value, dict):
            value = json.dumps(value)
        else:
            assert isinstance(json.loads(value), dict)


        return super(JSONDictField, self).get_db_prep_save(value, *args, **kwargs)

add_introspection_rules([], ["^common\.fields\.JSONDictField"])


class JSONListField(models.TextField):
    """JSONListField is a generic textfield that neatly  serializes/unserializes
JSON objects seamlessly"""

    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""

        if value == "":
            return []

        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            pass

        return value

    def get_db_prep_save(self, value, *args, **kwargs):
        """Convert our JSON object to a string before we save"""

        if value == "":
            return None

        if isinstance(value, list):
            value = json.dumps(value)
        else:
            assert isinstance(json.loads(value), list)

        return super(JSONListField, self).get_db_prep_save(value, *args, **kwargs)


add_introspection_rules([], ["^common\.fields\.JSONListField"])

class UUIDField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 64 )
        kwargs['blank'] = True
        models.CharField.__init__(self, *args, **kwargs)

    def pre_save(self, model_instance, add):
        if add and not getattr(model_instance,self.attname,None):
            value = str(uuid.uuid4())
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(models.CharField, self).pre_save(model_instance, add)


add_introspection_rules([], ["^common\.fields\.UUIDField"])

class QuerySetListField(models.TextField):
   description = " A field to serialize/deserialize and store a list of querysets"

   __metaclass__ = models.SubfieldBase

   def to_python(self, value):
       """
       Deserialize the value to back to a list of QuerySets 
       """
       if value == "" or value == None:
           return []
       try:
           if isinstance(value,basestring):
               deserialized_value = serializers.deserialize("json",value)
               return map(lambda x: x.object,deserialized_value )
       except ValueError:
          pass
       return value   

   def get_db_prep_save(self, value, *args, **kwargs):
       """
       Convert the list of QuerySets to a string by serializing
       """
       if value == "":
           return None
       if isinstance(value, list):
           value = serializers.serialize("json",value)
       return super(QuerySetListField, self).get_db_prep_save(value, *args, **kwargs)

add_introspection_rules([], ["^common\.fields\.QuerySetListField"])
