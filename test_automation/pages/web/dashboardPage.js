class WebDashboardPage {
  constructor(driver) {
    this.driver = driver;
    this.sidebarOverview = '#sidebar-overview';
    this.sidebarDraftRti = '#sidebar-draft-rti';
    this.sidebarTemplates = '#sidebar-templates';
    this.sidebarAiPolisher = '#sidebar-ai-polisher';
    this.sidebarScanner = '#sidebar-scanner';
    this.sidebarHistory = '#sidebar-history';
    this.sidebarChat = '#sidebar-chat';
    this.sidebarSettings = '#sidebar-settings';
    this.topSearchBar = '#global-intent-search';
    this.searchResultsOverlay = '.live-search-dropdown-overlay';
  }

  async navigateToSection(sectionId) {
    const el = await this.driver.findElement({ css: sectionId });
    await el.click();
  }

  async typeSearchQuery(query) {
    const search = await this.driver.findElement({ css: this.topSearchBar });
    await search.clear();
    await search.sendKeys(query);
  }

  async isSearchResultOverlayVisible() {
    try {
      const overlay = await this.driver.findElement({ css: this.searchResultsOverlay });
      return await overlay.isDisplayed();
    } catch {
      return false;
    }
  }

  async setViewportSize(width, height) {
    await this.driver.manage().window().setRect({ width, height });
  }
}

module.exports = WebDashboardPage;
