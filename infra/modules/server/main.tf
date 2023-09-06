# provider -> loginkey -> vpc data, subnet data -> ACG
# -> ACG rule -> init script -> network interface
# -> main interface

terraform {
  required_providers {
    ncloud = {
      source = "NaverCloudPlatform/ncloud"
    }
  }
  required_version = ">= 0.13"
}

provider "ncloud" {
  access_key  = var.NCP_ACCESS_KEY
  secret_key  = var.NCP_SECRET_KEY
  region      = var.region
  site        = var.site
  support_vpc = var.support_vpc
}

resource "ncloud_login_key" "loginkey" {
  key_name = "sns-${var.name}key-${var.env}"
}

data "ncloud_vpc" "main" {
  id = var.vpc_id
}

data "ncloud_subnet" "main" {
  id = var.subnet_be_server
}

resource "ncloud_access_control_group" "main" {
  name        = "sns-${var.name}-${var.env}"
  description = "${var.name} ACG"
  vpc_no      = data.ncloud_vpc.main.vpc_no
}

resource "ncloud_access_control_group_rule" "main" {
  access_control_group_no = ncloud_access_control_group.main.id

  inbound {
    protocol    = "TCP"
    ip_block    = "0.0.0.0/0"
    port_range  = var.acg_port_range
    description = "accept ${var.name} port for ${var.name}"
  }
}

resource "ncloud_init_script" "main" {
  name    = "set-${var.name}-${var.env}-tf"
  content = templatefile("${path.module}/${var.init_script_path}", var.init_script_envs)
}

resource "ncloud_network_interface" "main" {
    name                  = "${var.name}-nic-${var.env}"
    description           = "for ${var.name} server"
    subnet_no             = var.subnet_be_server
    access_control_groups = [
        data.ncloud_vpc.main.default_access_control_group_no, # default ACG
        ncloud_access_control_group.main.id, # created ACG
    ]
}

resource "ncloud_server" "main" {
  subnet_no                 = var.subnet_be_server
  name                      = "${var.name}-server-${var.env}"
  server_image_product_code = "SW.VSVR.OS.LNX64.UBNTU.SVR2004.B050"
  server_product_code       = var.server_product_code
  login_key_name            = ncloud_login_key.loginkey.key_name
  init_script_no = ncloud_init_script.main.id

  network_interface {
    network_interface_no = ncloud_network_interface.main.id
    order = 0
  }
}