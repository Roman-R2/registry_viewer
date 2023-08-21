class LoginGenerator{

    usernameEl = document.querySelector('#id_username');

    lastNameEl = document.querySelector('#id_last_name');
    firstNameEl = document.querySelector('#id_first_name');
    patronymicEl = document.querySelector('#id_patronymic');

    passwordGenerateButtonEl = document.querySelector('#password_generate_button');
    idPassword1El = document.querySelector('#id_password1');
    idPassword2El = document.querySelector('#id_password2');

    init() {
//        this.usernameEl.setAttribute('disabled', '');
        this.usernameEl.classList.add("no_border_input");
        this.addEventsForLoginGenerate();
        this.addEventsForGeneratePasswords();
    }

    addEventsForGeneratePasswords() {
        this.passwordGenerateButtonEl.addEventListener('click', ({target}) => {
            let generatedPassword = this.generatePassword(12);
            console.log('Сгенерированный пароль:', generatedPassword)
            this.idPassword1El.value = generatedPassword
            this.idPassword2El.value = generatedPassword
        });
    }

    addEventsForLoginGenerate(){
        this.lastNameEl.addEventListener('input', ({target}) => {
            this.generateLogin();
        });
        this.firstNameEl.addEventListener('input', ({target}) => {
            this.generateLogin();
        });
        this.patronymicEl.addEventListener('input', ({target}) => {
            this.generateLogin();
        });
    }

    replaceAll(string, search, replace) {
        return string.split(search).join(replace);
    }

    mainReplacer(value) {
        let result = this.replaceAll(value, 'Ё', 'E');
        result = this.replaceAll(result, 'Ж', 'ZH');
        result = this.replaceAll(result, 'Х', 'KH');
        result = this.replaceAll(result, 'Ц', 'TS');
        result = this.replaceAll(result, 'Ч', 'CH');
        result = this.replaceAll(result, 'Ш', 'SH');
        result = this.replaceAll(result, 'Щ', 'SCH');
        result = this.replaceAll(result, 'Ъ', '');
        result = this.replaceAll(result, 'Ь', '');
        result = this.replaceAll(result, 'Ю', 'YU');
        result = this.replaceAll(result, 'Я', 'YA');
        result = this.replaceAll(result, 'ё', 'e');
        result = this.replaceAll(result, 'ж', 'zh');
        result = this.replaceAll(result, 'х', 'kh');
        result = this.replaceAll(result, 'ц', 'ts');
        result = this.replaceAll(result, 'ч', 'ch');
        result = this.replaceAll(result, 'ш', 'sh');
        result = this.replaceAll(result, 'щ', 'sch');
        result = this.replaceAll(result, 'ъ', '');
        result = this.replaceAll(result, 'ь', '');
        result = this.replaceAll(result, 'ю', 'yu');
        result = this.replaceAll(result, 'я', 'ya');

        result = this.replaceAll(result, "А", "A");
        result = this.replaceAll(result, "Б", "B");
        result = this.replaceAll(result, "В", "V");
        result = this.replaceAll(result, "Г", "G");
        result = this.replaceAll(result, "Д", "D");
        result = this.replaceAll(result, "Е", "E");
        result = this.replaceAll(result, "З", "Z");
        result = this.replaceAll(result, "И", "I");
        result = this.replaceAll(result, "Й", "J");
        result = this.replaceAll(result, "К", "K");
        result = this.replaceAll(result, "Л", "L");
        result = this.replaceAll(result, "М", "M");
        result = this.replaceAll(result, "Н", "N");
        result = this.replaceAll(result, "О", "O");
        result = this.replaceAll(result, "П", "P");
        result = this.replaceAll(result, "Р", "R");
        result = this.replaceAll(result, "С", "S");
        result = this.replaceAll(result, "Т", "T");
        result = this.replaceAll(result, "У", "U");
        result = this.replaceAll(result, "Ф", "F");
        result = this.replaceAll(result, "Ы", "Y");
        result = this.replaceAll(result, "Э", "E");
        result = this.replaceAll(result, "а", "a");
        result = this.replaceAll(result, "б", "b");
        result = this.replaceAll(result, "в", "v");
        result = this.replaceAll(result, "г", "g");
        result = this.replaceAll(result, "д", "d");
        result = this.replaceAll(result, "е", "e");
        result = this.replaceAll(result, "з", "z");
        result = this.replaceAll(result, "и", "i");
        result = this.replaceAll(result, "й", "j");
        result = this.replaceAll(result, "к", "k");
        result = this.replaceAll(result, "л", "l");
        result = this.replaceAll(result, "м", "m");
        result = this.replaceAll(result, "н", "n");
        result = this.replaceAll(result, "о", "o");
        result = this.replaceAll(result, "п", "p");
        result = this.replaceAll(result, "р", "r");
        result = this.replaceAll(result, "с", "s");
        result = this.replaceAll(result, "т", "t");
        result = this.replaceAll(result, "у", "u");
        result = this.replaceAll(result, "ф", "f");
        result = this.replaceAll(result, "ы", "y");
        result = this.replaceAll(result, "э", "e");

        return result
    }

    toTitleCase(str) {
      return str.replace(
        /\w\S*/g,
        function(txt) {
          return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        }
      );
    }

    generateLogin() {
        let lastNameReplaced = this.toTitleCase(this.mainReplacer(this.lastNameEl.value))
        let firstLetterFirstName = ""
        let firstLetterPatronymic = ""

        if (this.firstNameEl.value.length != 0) {
            firstLetterFirstName = this.mainReplacer(Array.from(this.firstNameEl.value)[0]).toUpperCase();
        }

        if (this.patronymicEl.value.length != 0) {
            firstLetterPatronymic = this.mainReplacer(Array.from(this.patronymicEl.value)[0]).toUpperCase();
        }

        this.usernameEl.value = '027' + lastNameReplaced + firstLetterFirstName + firstLetterPatronymic;
    }

    generatePassword(length) {
            let charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
            let retVal = "";
        for (var i = 0, n = charset.length; i < length; ++i) {
            retVal += charset.charAt(Math.floor(Math.random() * n));
        }
        return retVal;
    }
}