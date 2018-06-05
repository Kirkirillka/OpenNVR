CAM_DELETED = {'type': 'success',
               'message': 'Camera was successfully deleted. Please,reload this page for further investigation.'
               }

CAM_ADDED={'type':'success',
           'message':'You added a new video source. Please, reload this page to see that stream.'}

REINITILAZE={'type':'success',
             'message':'You reinitilized your OpenNVR configuration.Some new sources might be added.'}

UPDATE_CONFIG={'type':'info',
               'message':'Configuration updated.'}

ERROR={'type':'error',
       'message':'Some error occured. Contact to developers to send bug info.'}


USER_ADD_FAILED={'type':'error',
                  'message':'Unable to add new user. Please, check supplied data.'}

USER_ADD_SUCCESS={'type':'success',
                  'message':'A new user was added onto system. Now he is allowed to authenticate.'}

USER_UPDATE_FAILED={'type':'error',
                    'message':'Cannot update user with supplied data'}

USER_UPDATE_SUCCESS={'type':'success',
                     'message':'User\' configuration updated.'}


USER_DELETE_FAILED={'type':'error',
                     'message':'Cannot delete this user'}

USER_DELETE_SUCCESS={'type':'success',
                     'message':'User was deleted'}


USER_PASSWORD_CHANGE_SUCCESS={'type':'success',
                     'message':'User\s password was updated!'}

USER_PASSWORD_CHANGE_FAILED={'type':'error',
                     'message':'Cannot update user password'}

SERVICE_RESTART_SUCCESS={'type':'success',
                     'message':'OpenNVR successfully restarted. All services are online'}

SERVICE_RESTART_FAILED={'type':'error',
                     'message':'Service restart attempt failed'}



NO_ACTION={'type':'info',
           'message':'No supported action supplied. Please, check our API for futher interaction'}