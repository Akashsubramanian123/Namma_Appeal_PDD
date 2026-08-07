class AuthPage {
  constructor(driver) {
    this.driver = driver;
    this.emailInput = '~auth_email_field';
    this.passwordInput = '~auth_password_field';
    this.loginButton = '~auth_login_button';
    this.registerButton = '~auth_register_button';
    this.profileAvatar = '~home_profile_avatar';
    this.errorMessageText = '~auth_error_message';
    this.logoutButton = '~drawer_logout_button';
  }

  async enterEmail(email) {
    // Works with Flutter Driver key / UiAutomator2 accessibility ID
    const el = await this.driver.$(this.emailInput);
    await el.setValue(email);
  }

  async enterPassword(password) {
    const el = await this.driver.$(this.passwordInput);
    await el.setValue(password);
  }

  async clickLogin() {
    const el = await this.driver.$(this.loginButton);
    await el.click();
  }

  async isLoggedIn() {
    try {
      const avatar = await this.driver.$(this.profileAvatar);
      return await avatar.isDisplayed();
    } catch {
      return false;
    }
  }

  async getErrorMessage() {
    const err = await this.driver.$(this.errorMessageText);
    return await err.getText();
  }

  async logout() {
    const btn = await this.driver.$(this.logoutButton);
    await btn.click();
  }
}

module.exports = AuthPage;
