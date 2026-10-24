"""WhatsApp management contract."""

from saba.channels._manifest import DIRECT_GROUP_POLICIES, field
from saba.channels.contracts import ChannelManagementSpec, ChannelSetupSpec
from saba.channels.plugin import ChannelPlugin
from saba.channels.whatsapp.state import local_state_present
from saba.channels.whatsapp.validation import validate

SETUP_SPEC = ChannelSetupSpec(
    fields={
        "useProxy": field("bool", default=False),
        "allowFrom": field("list", snapshot=False),
        "groupPolicy": field(
            "enum",
            choices=DIRECT_GROUP_POLICIES,
            default="open",
            snapshot=False,
        ),
        "databasePath": field(writable=False, snapshot=False),
        "lidMappings": field("json", writable=False, snapshot=False),
    },
    official_url="https://faq.whatsapp.com/",
    validator=validate,
)

PLUGIN = ChannelPlugin(
    name="whatsapp",
    display_name="WhatsApp",
    runtime=f"{__package__}.runtime:WhatsAppChannel",
    connector=f"{__package__}.connect:WhatsAppConnectStore",
    setup=SETUP_SPEC,
    management=ChannelManagementSpec(local_state_present=local_state_present),
    dependencies=(),
    default_enabled=True,
    webui="webui/index.tsx",
)
