
def GetMenu(user):
    result = []
    if user == '' :
        result.append(
            {
                "text": 'Sign In',
                "url": '/signin',
                "linkAttr": {
                    "rel": 'noopener'
                }
            }
        )
    else :
        result.append(
            {
                "text": 'Logout',
                "url": '/logoutUser',
                "linkAttr": {
                    "rel": 'noopener'
                }
            }
        )
        result.append(
            {
                "text": 'Profile: ' + user,
                "url": '/briefcase',
                "linkAttr": {
                    "rel": 'noopener'
                }
            }
        )

    result.append(
        {
            "text": 'About',
            "url": '/about',
            "linkAttr": {
                "rel": 'noopener'
            }
        }
    )
    result.append(
        {
            "text": 'Contacts',
            "url": '/contacts',
             "linkAttr": {
                "rel": 'noopener'
            }
         }
    )   

    result.append(
        {
            "text": 'Home',
            "url": '/',
            "linkAttr": {
                "rel": 'noopener'
            }
        }
    ) 
    return result