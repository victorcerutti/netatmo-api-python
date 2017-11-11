"""
coding=utf-8
"""
import time

from . import NoDevice, postRequest, _BASE_URL

_SETTEMP_REQ = _BASE_URL + "api/setthermpoint"
_GETTHERMOSTATDATA_REQ = _BASE_URL + "api/getthermostatsdata"


class ThermostatData:
    """
    List the Thermostat devices (relays and thermostat modules)

    Args:
        authData (ClientAuth):
                Authentication information with a working access Token
    """
    def __init__(self, authData):
        self.getAuthToken = authData.accessToken
        postParams = {
                "access_token": self.getAuthToken
                }
        resp = postRequest(_GETTHERMOSTATDATA_REQ, postParams)

        self.rawData = resp['body']
        self.devices = {d['_id']: d for d in self.rawData['devices']}
        if not self.devices:
            raise NoDevice("No thermostat available")
        self.modules = dict()
        self.therm_program_list = dict()
        self.zones = dict()
        self.timetable = dict()
        for i in range(len(self.rawData['devices'])):
            nameDevice = self.rawData['devices'][i]['station_name']
            if nameDevice not in self.modules:
                self.modules[nameDevice] = dict()
            for m in self.rawData['devices'][i]['modules']:
                self.modules[nameDevice][m['_id']] = m
            for p in self.rawData['devices'][i]['modules'][
                    0]['therm_program_list']:
                self.therm_program_list[p['program_id']] = p
            for z in self.rawData['devices'][i]['modules'][
                    0]['therm_program_list'][0]['zones']:
                self.zones[z['id']] = z
            for o in self.rawData['devices'][i]['modules'][
                    0]['therm_program_list'][0]['timetable']:
                self.timetable[o['m_offset']] = o
        self.default_device = list(self.devices.values())[0]['station_name']

        self.default_module = list(
            self.modules[self.default_device].values())[0]
        # print(self.therm_program_list)
        # print(self.devices)
        # print(self.modList)

    def deviceById(self, did):
        # print('deviceById')
        return None if did not in self.devices else self.devices[did]

    def deviceByName(self, device=None):
        # print('deviceByName')
        if not device:
            device = self.default_device
        for key, value in self.devices.items():
            if value['station_name'] == device:
                return self.devices[key]

    def moduleById(self, mid):
        # print('moduleById')
        for device, mod in self.modules.items():
            if mid in self.modules[device]:
                return self.modules[device][mid]
        return None

    def moduleByName(self, module=None, device=None):
        # print('moduleByName')
        if not module and not device:
            return self.default_module
        elif device and module:
            if device not in self.modules:
                return None
            for mod_id in self.modules[device]:
                if self.modules[device][mod_id]['module_name'] == module:
                    return self.modules[device][mod_id]
        elif not device and module:
            for device, mod_ids in self.modules.items():
                for mod_id in mod_ids:
                    if self.modules[device][mod_id]['module_name'] == module:
                        return self.modules[device][mod_id]
        else:
            return list(self.modules[device].values())[0]
        return None

    def setpoints(self, module=None, device=None, mid=None):
        """
        Return the setpoint of a given module.
        """
        # print('setpoints')
        setpoint = None
        if mid:
            module_data = self.moduleById(mid)
            # print('mid')
        else:
            module_data = self.moduleByName(device=device, module=module)
            # print('iets')
        if module_data:
            print(module_data)
            if module_data['setpoint']['setpoint_mode'] == 'manual':
                setpoint = module_data['setpoint']['setpoint_temp']
            # elif module_data['setpoint']['setpoint_mode'] == 'program':
            #     setpoint = module_data['measured']['setpoint_temp']
            else:
                setpoint = module_data['measured']['setpoint_temp']
            # setpoint = module_data['setpoint']['setpoint_temp']
        return setpoint

    def away(self, module=None, device=None, mid=None):
        """
        Return the setpoint of a given module.
        """
        away = None
        if mid:
            module_data = self.moduleById(mid)
        else:
            module_data = self.moduleByName(device=device, module=module)
        if module_data:
            away = module_data['setpoint']['setpoint_mode']
        return away

    def currentTemp(self, module=None, device=None, mid=None):
        """
        Return the current temperature of a given module.
        """
        # print('currentTemp')
        current_temp = None
        if mid:
            # print('id')
            module_data = self.moduleById(mid)
            # print(module_data)
        else:
            # print('anders')
            module_data = self.moduleByName(device=device, module=module)
            # print(module_data)
        if module_data:
            # print(module_data)
            current_temp = module_data['measured']['temperature']
        return current_temp

    def operation(self, module=None, device=None, mid=None):
        """
        Return the operation (therm_relay_cmd) of a given device.
        """
        # print('operation')
        operation = None
        if mid:
            # print('mid')
            module_data = self.moduleById(mid)
        else:
            # print('else')
            module_data = self.moduleByName(device=device, module=module)
        if module_data:
            operation = module_data['therm_relay_cmd']
        # print(module_data)
        # print(operation)
        return operation

    def currentProgram(self, module=None, device=None, mid=None):
        """
        Return the current program  of a given device.
        """
        program = None
        if mid:
            # print('mid')
            module_data = self.moduleById(mid)
        else:
            # print('else')
            module_data = self.moduleByName(device=device, module=module)
        if module_data:
            if module_data['therm_program_list']['selected']:
                program = module_data['therm_program_list']['name']
        return program

    # def currentZone(self, module=None, device=None, mid=None):
    #     """
    #     Return the current zone.
    #     """
    #     current_zone = None
    #     if mid:
    #         module_data = self.moduleById(mid)
    #     else:
    #         module_data = self.moduleByName(device=device, module=module)
    #     if module_data:
    #         current_zone =

    def setthermpoint(self, mode, temp, endTimeOffset, device_id, module_id):
        postParams = {
            "access_token": self.getAuthToken,
            "device_id": device_id,
            "module_id": module_id,
            "setpoint_mode": mode
            }
        # print(device_id)
        # print(module_id)
        # postParams['device_id'] = device_id
        # postParams['module_id'] = module_id
        # postParams['setpoint_mode'] = mode
        if mode == "manual":
            postParams["setpoint_endtime"] = time.time() + endTimeOffset
            postParams["setpoint_temp"] = temp
        return postRequest(_SETTEMP_REQ, postParams)
