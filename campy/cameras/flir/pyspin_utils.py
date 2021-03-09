import PySpin
import numpy as np

""" --------------- helpful wrapper functions for PySpin on camera level---------------"""

# dicts that help understand which PySpin numbers relate to what
_rw_modes = {
   PySpin.RO: "read only",
   PySpin.RW: "read/write",
   PySpin.WO: "write only",
   PySpin.NA: "not available"
}

_attr_types = {
   PySpin.intfIFloat: PySpin.CFloatPtr,
   PySpin.intfIBoolean: PySpin.CBooleanPtr,
   PySpin.intfIInteger: PySpin.CIntegerPtr,
   PySpin.intfIEnumeration: PySpin.CEnumerationPtr,
   PySpin.intfIString: PySpin.CStringPtr,
}

_attr_type_names = {
   PySpin.intfIFloat: 'float',
   PySpin.intfIBoolean: 'bool',
   PySpin.intfIInteger: 'int',
   PySpin.intfIEnumeration: 'enum',
   PySpin.intfIString: 'string',
   PySpin.intfICommand: 'command',
}

def get_val(name,nodemap):
    """
    Get the value from one node in the nodemap

    Parameters
    ----------
    name : string
        Name of the node..
    nodemap : PySpin nodemap
        The nodemap to access.

    Raises
    ------
    ValueError
        If no value was found in node.

    Returns
    -------
    Int or str depending on node
        Value.

    """
    #nodemap = camera.GetTLDeviceNodeMap()
    cur_ptr = get_node_ptr(name,nodemap)

    if hasattr(cur_ptr,"GetValue"):
        return cur_ptr.GetValue()
    elif hasattr(cur_ptr,"ToString"):
        return cur_ptr.ToString()
    elif hasattr(cur_ptr,"GetIntValue"):
        return cur_ptr.GetIntValue()
    else:
        raise ValueError("Value not forund in node attributes")


def get_info(name,nodemap):
    """
    get info dict about a node in nodemap

    Parameters
    ----------
    name : string
        Name of the node.
    nodemap : PySpin nodemap
        The nodemap to access.

    Returns
    -------
    dict
        contains info of node

    """
    #nodemap = camera.GetTLDeviceNodeMap()

    info = {'name': name}


    try:
        cur_node = nodemap.GetNode(name)
        if not PySpin.IsAvailable(cur_node) or not PySpin.IsReadable(cur_node):
            raise ValueError("'%s' is not readable " % name)

        interface_type = cur_node.GetPrincipalInterfaceType()
        cur_ptr = _attr_types[interface_type](cur_node)

        if hasattr(cur_ptr, 'GetAccessMode'):
            access = cur_ptr.GetAccessMode()
            info['access'] = _rw_modes.get(access, access)
            # print(info['access'])
            if isinstance(info['access'], str) and 'read' in info['access']:
                info['value'] = get_val(name, nodemap)

        info['description'] = cur_ptr.GetDescription()
        info['type'] = _attr_type_names[interface_type]

    except PySpin.SpinnakerException as ex:
        raise ValueError("'%s' is not a camera method or attribute - %s" % (name,ex))

    return info

def get_node_ptr(name,nodemap,for_writing=False):
    """
    This function returns the pointer to a node for reading or writing

    Parameters
    ----------
    name : string
        Name of the node.
    nodemap : PySpin nodemap
        The nodemap to access.
    for_writing : BOOL, optional
        If true checks if node is writeble, if false it checks if it is readable.
        The default is False.

    Raises
    ------
    ValueError
        If node is not available or not readable/writable depending on for_writing.

    Returns
    -------
    PySpin pointer to node
        It uses the global _attr_types dict to find the right pointer type.

    """
    #nodemap = camera.GetTLDeviceNodeMap()
    
    cur_node = nodemap.GetNode(name)
    if for_writing:
        if not PySpin.IsAvailable(cur_node) or not PySpin.IsWritable()(cur_node):
            raise ValueError("'%s' is not writable " % name)

    else:
        if not PySpin.IsAvailable(cur_node) or not PySpin.IsReadable(cur_node):
            raise ValueError("'%s' is not readable " % name)

    interface_type = cur_node.GetPrincipalInterfaceType()
    return _attr_types[interface_type](cur_node)



