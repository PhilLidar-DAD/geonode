var config = {
        tools: [
            {
                ptype: "gxp_wmsgetfeatureinfo",
                format: "grid",
                actionTarget: "main.tbar",
                outputConfig: {width: 400, height: 200, panIn: false}
            },
        ],
        {% if PROXY_URL %}
        proxy: '{{ PROXY_URL }}',
        {% endif %}
        localGeoServerBaseUrl: "{{GEOSERVER_BASE_URL}}",
        authorizedRoles: "{{ user.is_authenticated|yesno:"ROLE_ADMINISTRATOR,ROLE_ANONYMOUS" }}",

        /* The URL to a REST map configuration service.  This service 
         * provides listing and, with an authenticated user, saving of 
         * maps on the server for sharing and editing.
         */
        rest: "/maps/",
        {% if MAPFISH_PRINT_ENABLED %}
        printService: "{{GEOSERVER_BASE_URL}}pdf/",
        {% else %}
        printService: "",
        {% endif %}
        
        portalConfig: {
            renderTo: "preview_map",
            height: 400 
        },

        listeners: {
            "ready": function() {
                var map = app.mapPanel.map;
                var layer = app.map.layers.slice(-1)[0];

                // FIXME(Ariel): Zoom to extent until #1795 is fixed.
                //map.zoomToExtent(layer.maxExtent, false)
                
                var bbox = layer.bbox;
                if (bbox != undefined)
                {
                   if (!Array.isArray(bbox) && Object.keys(layer.srs) in bbox) {
                    bbox = bbox[Object.keys(layer.srs)].bbox;
                   }

                   var extent = OpenLayers.Bounds.fromArray(bbox);
                   var zoomToData = function()
                   {
                       map.zoomToExtent(extent, false);
                       app.mapPanel.center = map.center;
                       app.mapPanel.zoom = map.zoom;
                       map.events.unregister('changebaselayer', null, zoomToData);
                   };
                   map.events.register('changebaselayer',null,zoomToData);
                   if(map.baseLayer){
                    map.zoomToExtent(extent, false);
                   }
                }
            },
            "beforeunload": function() {
                if (modified) {
                    styleEditor.show();
                    return false;
                }
            }
        }
    };
    

tools: [{
            ptype: "gxp_wmsgetfeatureinfo",
            format: "grid",
            actionTarget: "main.tbar",
            outputConfig: {width: 400, height: 200, panIn: false}
        },
        {
            ptype: "gxp_featuremanager",
            id: "feature_manager",
            autoSetLayer: true,
            actionTarget: "main.tbar"
        },
        {
            ptype: "gxp_featureeditor",
            id: "feature_manager",
            autoLoadFeature: true,
            actionTarget: "main.tbar"
        }],
