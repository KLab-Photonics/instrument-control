from Device_Drivers.stellarnet_driverLibs import stellarnet_driver3 as sn

connection = sn.deviceConnectionCheck(0)
print("Connection status:", connection)


device_info = sn.print_info(0)
print("Device Info:", device_info)

device_connection = sn.deviceConnectionCheck(0)
print("Device Connection Status:", device_connection)

device_ID = sn.getDeviceId(0)
print("Device ID:", device_ID)

total_device_count_num = sn.total_device_count()
print("Total Device Count:", total_device_count_num)

device_version = sn.version()
print("Device Version:", device_version)

device_id = sn.getFullDeviceID(0)
print("Full Device ID:", device_id)


