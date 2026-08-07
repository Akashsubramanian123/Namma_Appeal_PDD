class RejectionScannerPage {
  constructor(driver) {
    this.driver = driver;
    this.scannerTab = '~nav_tab_rejection_scanner';
    this.cameraButton = '~scanner_camera_picker';
    this.galleryButton = '~scanner_gallery_picker';
    this.extractedTextContainer = '~ocr_extracted_text';
    this.adjudicationScoreBadge = '~ml_win_probability_score';
    this.softBlockWarningBanner = '~soft_block_warning_banner';
    this.processDocumentButton = '~scanner_process_btn';
  }

  async openScanner() {
    const tab = await this.driver.$(this.scannerTab);
    await tab.click();
  }

  async selectGalleryImage() {
    const btn = await this.driver.$(this.galleryButton);
    await btn.click();
  }

  async triggerProcessDocument() {
    const btn = await this.driver.$(this.processDocumentButton);
    await btn.click();
  }

  async getExtractedText() {
    const el = await this.driver.$(this.extractedTextContainer);
    return await el.getText();
  }

  async getWinProbabilityScore() {
    const el = await this.driver.$(this.adjudicationScoreBadge);
    const scoreStr = await el.getText();
    return parseFloat(scoreStr.replace(/[^0-9.]/g, ''));
  }

  async isSoftBlockWarningVisible() {
    try {
      const banner = await this.driver.$(this.softBlockWarningBanner);
      return await banner.isDisplayed();
    } catch {
      return false;
    }
  }
}

module.exports = RejectionScannerPage;
