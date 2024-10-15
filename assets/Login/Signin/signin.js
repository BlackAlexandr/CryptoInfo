$(() => {
    const formData = {
        mail: '',
        psw: ''
      };

  
    const changePasswordMode = function (name) {
      const editor = formWidget.getEditor(name);
      editor.option('mode', editor.option('mode') === 'text' ? 'password' : 'text');
    };
  
    const formWidget = $('#form').dxForm({
      formData,
      readOnly: false,
      showColonAfterLabel: true,
      showValidationSummary: true,
      items: [{
        itemType: 'group',
        items: [{
          dataField: 'Email',
          name: 'mail',
          editorOptions: {
            valueChangeEvent: 'keyup',
          },
          validationRules: [{
            type: 'required',
            message: 'Email is required',
          }, {
            type: 'email',
            message: 'Email is invalid',
          }, {
            type: 'async',
            message: 'Email is already registered',
            validationCallback(params) {
              return sendRequest(params.value);
            },
          }],
        }, {
          dataField: 'Password',
          editorOptions: {
            mode: 'password',
            valueChangeEvent: 'keyup',
            onValueChanged() {
              const editor = formWidget.getEditor('ConfirmPassword');
              if (editor.option('value')) {
                editor.element().dxValidator('validate');
              }
            },
            buttons: [{
              name: 'password',
              location: 'after',
              options: {
                stylingMode: 'text',
                icon: 'eyeopen',
                onClick: () => changePasswordMode('Password'),
              },
            }],
          },
        }],
      },{
        itemType: 'group',
        cssClass: 'last-group',
        colCountByScreen: {
          xs: 2,
          sm: 2,
          md: 2,
          lg: 2,
        },
        items: [{
          label: {
            visible: false,
          },
        }, {
          itemType: 'group',
          cssClass: 'buttons-group',
          colCountByScreen: {
            xs: 2,
            sm: 2,
            md: 2,
            lg: 2,
          },
          items: [{

            itemType: 'button',
            buttonOptions: {
              text: 'Signin',
              type: 'default',
              useSubmitBehavior: true,
              width: '120px',
            },
          }],
        }],
      }],
    }).dxForm('instance');

  });
  