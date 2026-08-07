class RtiGeneratorPage {
  constructor(driver) {
    this.driver = driver;
    this.generatorTab = '~nav_tab_rti_generator';
    this.languageDropdown = '~rti_language_selector';
    this.departmentDropdown = '~rti_pio_department_selector';
    this.queryInputField = '~rti_query_input';
    this.generateButton = '~rti_generate_letter_btn';
    this.firstAppealToggle = '~rti_first_appeal_toggle';
    this.pdfExportButton = '~rti_export_pdf_btn';
    this.deadlineReminderBanner = '~active_deadline_reminder_banner';
  }

  async selectLanguage(lang) {
    const selector = await this.driver.$(this.languageDropdown);
    await selector.click();
    const langOption = await this.driver.$(`~lang_option_${lang.toLowerCase()}`);
    await langOption.click();
  }

  async selectDepartment(deptName) {
    const selector = await this.driver.$(this.departmentDropdown);
    await selector.click();
    const option = await this.driver.$(`~dept_option_${deptName}`);
    await option.click();
  }

  async enterQuery(queryText) {
    const input = await this.driver.$(this.queryInputField);
    await input.setValue(queryText);
  }

  async toggleFirstAppeal() {
    const toggle = await this.driver.$(this.firstAppealToggle);
    await toggle.click();
  }

  async generatePdf() {
    const btn = await this.driver.$(this.pdfExportButton);
    await btn.click();
  }

  async isDeadlineReminderActive() {
    try {
      const banner = await this.driver.$(this.deadlineReminderBanner);
      return await banner.isDisplayed();
    } catch {
      return false;
    }
  }
}

module.exports = RtiGeneratorPage;
