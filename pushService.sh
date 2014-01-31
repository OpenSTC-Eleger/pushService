#! /bin/sh
PUSH_SERVICE_PATH=/srv/openerp/push_service
sudo su - nonow_export_test -s /bin/bash
python $PUSH_SERVICE_PATH/push_service.py &> $PUSH_SERVICE_PATH/http_logs.log
