from flask import json

# TODO move into class but preserve format!
print_cmd = """^R375
^L
AD,24,48,2,2,0,0,{initial1}
AD,24,144,2,2,0,0,{initial2}
W108,24,5,2,Q,8,9,{length},0
{code}
AD,0,280,2,2,0,0,{name}
E
"""


class PrintJob:
    def __init__(self, code, scientist_name, sample_group_name, plant_name):
        self._code = code
        self._scientist_name = scientist_name
        self._sample_group_name = sample_group_name
        self._plant_name = plant_name

    def serialize(self):
        obj = dict()
        obj['code'] = self._code
        obj['scientist_name'] = self._scientist_name
        obj['sample_group_name'] = self._sample_group_name
        obj['plant_name'] = self._plant_name

        return json.dumps(obj)

    @classmethod
    def load(cls, obj):
        """
        Deserialize the given object to create an instance of :class:`PrintJob`

        :param obj: A serialized version of a :class:`PrintJob`

        :return: instance of the deserialized :class:`PrintJob`
        """
        map = json.loads(obj)
        return cls(map['code'], map['scientist_name'], map['sample_group_name'], map['plant_name'])

    def _compute_initials(self):
        parts = self._scientist_name.split(' ')
        if len(parts) == 1:
            return self._scientist_name[0], ' '
        else:
            return parts[0][0], parts[len(parts) - 1][0]

    def get_print_command(self):
        """
        Creates the command string for the printer to print the desired label with the information of this print job
        :return: The command string for the printer
        """
        initial1, initial2 = self._compute_initials()
        return print_cmd.format(initial1=initial1, initial2=initial2, code=self._code, name=self._plant_name,
                                length=len(self._code)).encode('utf-8')
