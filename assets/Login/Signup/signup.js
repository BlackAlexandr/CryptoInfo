$(() => {
  const formData = {
    Email: "",
    Password: "",
    Name: "",
    Country: "",
  };
  let validationMessage = '';

  const sendRequest = function (value) {
    const d = $.Deferred();
    $.ajax({
      type: "GET",
      url: "/checkingEmail",
      data: { mail: value },
    })
      .done(function (res) {
        if (res != "New") {
          d.reject(res);
        } else {
          d.resolve();
        }
      })
      .fail(function (Response) {
        //do something when any error occurs.
        console.log(Response);
      });

    return d.promise();
  };

  const changePasswordMode = function (name) {
    const editor = formWidget.getEditor(name);
    editor.option(
      "mode",
      editor.option("mode") === "text" ? "password" : "text"
    );
  };

  const formWidget = $("#form1")
    .dxForm({
      formData,
      readOnly: false,
      showColonAfterLabel: true,
      showValidationSummary: true,
      validationGroup: "customerData",
      onOptionChanged: (e) => {
        if (e.name === "isDirty") {
          const resetButton = formWidget.getButton("Reset");
          resetButton.option("disabled", !e.value);
        }
      },
      items: [
        {
          itemType: "group",
          items: [
            {
              dataField: "Name",
              editorOptions: {
                valueChangeEvent: "keyup",
              },
              validationRules: [
                {
                  type: "required",
                  message: "Name is required",
                },
                {
                  type: "pattern",
                  pattern: "^[^0-9]+$",
                  message: "Do not use digits in the Name",
                },
              ],
            },
            {
              dataField: "Email",
              editorOptions: {
                valueChangeEvent: "keyup",
              },
              validationRules: [
                {
                  type: "required",
                  message: "Email is required",
                },
                {
                  type: "email",
                  message: "Email is invalid",
                },
                {
                  type: "async",
                  message: "Email is already registered",
                  validationCallback(params) {
                    return sendRequest(params.value);
                  },
                },
              ],
            },
            {
              dataField: "Password",
              editorOptions: {
                mode: "password",
                valueChangeEvent: "keyup",
                onValueChanged() {
                  const editor = formWidget.getEditor("ConfirmPassword");
                  if (editor.option("value")) {
                    editor.element().dxValidator("validate");
                  }
                },
                buttons: [
                  {
                    name: "password",
                    location: "after",
                    options: {
                      stylingMode: "text",
                      icon: "eyeopen",
                      onClick: () => changePasswordMode("Password"),
                    },
                  },
                ],
              },
              validationRules: [
                {
                  type: "required",
                  message: "Password is required",
                },
                {
                  type: "stringLength",
                  min: 8,
                  message: "Password must have at least 8 symbols",
                },
                {
                  type: 'pattern',
                  pattern: /[a-z]+/,
                  message: 'At least one alphabet should be of Upper Case [A-Z]',
                },
                {
                  type: 'pattern',
                  pattern: /[A-Z]+/,
                  message: 'The alphabet must be between [a-z]',
                },
                {
                  type: 'pattern',
                  pattern: /[0-9]+/,
                  message: 'At least 1 number or digit between [0-9]',
                },
                {
                  type: 'pattern',
                  pattern: /[!@#$_]+/,
                  message: 'At least 1 character from [ _ or @ or $ or ! or #]',
                },
              ],
            },
            {
              name: "ConfirmPassword",
              dataField: "ConfirmPassword",
              label: {
                text: "Confirm Password",
              },
              editorType: "dxTextBox",
              editorOptions: {
                mode: "password",
                valueChangeEvent: "keyup",
                buttons: [
                  {
                    name: "password",
                    location: "after",
                    options: {
                      icon: "eyeopen",
                      stylingMode: "text",
                      onClick: () => changePasswordMode("ConfirmPassword"),
                    },
                  },
                ],
              },
              validationRules: [
                {
                  type: "required",
                  message: "Confirm Password is required",
                },
                {
                  type: "compare",
                  message: "'Password' and 'Confirm Password' do not match",
                  comparisonTarget() {
                    return formWidget.option("formData").Password;
                  },
                },
              ],
            },
            {
              dataField: "Country",
              editorOptions: {
                valueChangeEvent: "keyup",
              },
            },
          ],
        },

        {
          itemType: "group",
          cssClass: "last-group",

          items: [
            {
              label: {
                visible: false,
              },
            },
            {
              itemType: "group",
              cssClass: "buttons-group",

              items: [
                {
                  itemType: "button",
                  buttonOptions: {
                    text: "Register",
                    type: "default",
                    useSubmitBehavior: true,
                    width: "200px",
                  },
                },
              ],
            },
          ],
        },
      ],
    })
    .dxForm("instance");
});
