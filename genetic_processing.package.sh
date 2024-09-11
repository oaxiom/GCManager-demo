pyinstaller genetic_processing.py \
    --distpath . \
    --hidden-import=passlib.handlers.bcrypt \
    --hidden-import=python_multipart \
    --hidden-import=zmq \
    --hidden-import=py7zr \
    --hidden-import=psutil \
    --hidden-import=pkg_resources.py2_warn \
    --add-data "disDB/Pharma/*:disDB/Pharma" \
    --add-data "disDB/Risk/*:disDB/Risk" \
    --add-data "demo_data/PID.RESTRICTED1/*:demo_data/PID.RESTRICTED1" \
    --add-data "demo_data/PID.72210953309787/*:demo_data/PID.72210953309787" \
    --add-data "demo_data/PID.NA12878/*:demo_data/PID.NA12878" \
    --add-data "static_data/html/*:static_data/html" \
    --add-data "static_data/PharmaGKB/*:static_data/PharmaGKB" \
    --add-data "static_data/Risk/*:static_data/Risk" \
    --add-data "keys/*:keys" \
    --add-data "manual/*:manual"