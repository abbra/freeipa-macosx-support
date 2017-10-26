# Authors:
#   Alexander Bokovoy <ab@vda.li>
#
# see file 'COPYING' for use and warranty information

import re

from ipalib import api, errors
from ipalib import Str, StrEnum, Bool, Bytes, Int
from ipalib.plugable import Registry
from .baseldap import (
    pkey_to_value,
    LDAPObject,
    LDAPCreate,
    LDAPDelete,
    LDAPUpdate,
    LDAPSearch,
    LDAPRetrieve,
    LDAPQuery,
    LDAPAddMember,
    LDAPRemoveMember)
from ipalib import _, ngettext
from ipalib import output
from ipapython.dn import DN

__doc__ = _("""
Mac OS X configuration management for FreeIPA

Define and distribute profile configuration for Mac OS X clients

EXAMPLES:

 Enable Mac OS X support in FreeIPA. Defines default configuration settings
 that allow Mac OS X clients to be configured to use all existing FreeIPA masters 
 for identity information and Kerberos authentication:

   ipa macosx-enable

 Show current configuration, optionally save JSON property list in a file:

   ipa macosx-show [--out=profile.json]

 Import new configuration from a JSON property list format:

   ipa macosx-import --data=profile.json

""")

register = Registry()

# Mac OS X clients actually search over all LDAP naming contexts with LDAP
# filter "(&(objectClass=organizationalUnit)(ou=macosxodconfig))" and request a
# single attribute "description", so the config can be placed anywhere.
#
# Configuration is stored in ou=macosxodconfig,cn=opendirectory,cn=etc,$SUFFIX
#
# If DN for container is going to change, then updates/60-macosx.update need to
# be changed as well, as it defines actual LDAP objects and ACIs to access them.
PLUGIN_CONFIG = (
    ('container_macosx', DN(('ou', 'macosxodconfig'), ('cn', 'opendirectory'), ('cn', 'etc'))),
)

@register()
class macosx(LDAPObject):
    """
    Mac OS X client management profile 
    """
    container_dn = None
    object_name = _('Mac OS X client profile')
    object_name_plural = _('Mac OS X client profiles')
    object_class = ['organisationalUnit', 'apple-configuration']
    permission_filter_objectclasses = ['apple-configuration']
    default_attributes = [
        'ou',
        'description', 
    ]
    search_display_attributes = [
        'ou', 'description',
    ]
    rdn_is_primary_key = True

    managed_permissions = {
        'System: Manage Mac OS X Client Profile': {
            'ipapermbindruletype': 'permission',
            'ipapermright': {'write'},
            'ipapermdefaultattr': {
                'description',
            },
            'default_privileges': {'Mac OS X Client Profile Administrators'},
        },
    }

    label = _('Mac OS X Client Profile')
    label_singular = _('Mac OS X Client Profile')

    takes_params = (
        Bytes('description',
            cli_name='data',
            label=_('JSON data for profile'),
            flags = ['no_display', 'no_create', 'no_search', 'no_update'],
        ),
    )
    
    # Inject constants into the api.env before it is locked down
    def _on_finalize(self):
        self.env._merge(**dict(PLUGIN_CONFIG))
        self.container_dn = self.env.container_macosx
        super(macosx, self)._on_finalize()

    def get_dn(self, *keys, **kwargs):
        return DN(self.container_dn, api.env.basedn)

@register()
class macosx_enable(Command):
    __doc__ = _('Create a new Desktop Profile.')

    msg_summary = _('Added Desktop Profile "%(value)s"')



@register()
class macosx_disable(Command):
    __doc__ = _('Delete a Desktop Profile.')

    msg_summary = _('Deleted Desktop Profile "%(value)s"')



@register()
class macosx_import(LDAPUpdate):
    __doc__ = _('Import a Mac OS X Client Profile.')

    msg_summary = _('Imported Mac OS X Client Profile"%(value)s"')



@register()
class macosx_show(LDAPRetrieve):
    __doc__ = _('Display the properties of Mac OS X Client Profile.')


