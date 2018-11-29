/* globals gettext */
/* eslint-disable react/no-danger, import/prefer-default-export */
import React from 'react';
import PropTypes from 'prop-types';
import { Button, Icon, StatusAlert } from '@edx/paragon/static';
import StringUtils from 'edx-ui-toolkit/js/utils/string-utils';
import StudentAccountDeletionModal from './StudentAccountDeletionModal';

export class StudentAccountDeletion extends React.Component {
  constructor(props) {
    super(props);
    this.closeDeletionModal = this.closeDeletionModal.bind(this);
    this.loadDeletionModal = this.loadDeletionModal.bind(this);
    this.state = {
      deletionModalOpen: false,
      isActive: props.isActive,
      socialAuthConnected: this.getConnectedSocialAuth(),
    };
  }

  getConnectedSocialAuth() {
    const { socialAccountLinks } = this.props;
    if (socialAccountLinks && socialAccountLinks.providers) {
      return socialAccountLinks.providers.reduce((acc, value) => acc || value.connected, false);
    }

    return false;
  }

  closeDeletionModal() {
    this.setState({ deletionModalOpen: false });
    this.modalTrigger.focus();
  }

  loadDeletionModal() {
    this.setState({ deletionModalOpen: true });
  }

  render() {
    const { deletionModalOpen, socialAuthConnected, isActive } = this.state;
    const loseAccessText = StringUtils.interpolate(
      gettext('As we mentioned before, we will lose your certificates obtained in the courses/specializations; and in that sense access to them. That is why we invite you to {htmlStart}obtain a copy of these certificates to keep the support of having studied with us {htmlEnd}and of the skills obtained.'),
      {
        htmlStart: '<a href="http://edx.readthedocs.io/projects/edx-guide-for-students/en/latest/SFD_certificates.html#printing-a-certificate" target="_blank">',
        htmlEnd: '</a>',
      },
    );

    const showError = socialAuthConnected || !isActive;

    const socialAuthError = StringUtils.interpolate(
      gettext('Before proceeding, please {htmlStart}unlink all social media accounts{htmlEnd}.'),
      {
        htmlStart: '<a href="https://support.edx.org/hc/en-us/articles/207206067" target="_blank">',
        htmlEnd: '</a>',
      },
    );

    const activationError = StringUtils.interpolate(
      gettext('Before proceeding, please {htmlStart}activate your account{htmlEnd}.'),
      {
        htmlStart: '<a href="https://support.edx.org/hc/en-us/articles/115000940568-How-do-I-activate-my-account-" target="_blank">',
        htmlEnd: '</a>',
      },
    );

    return (
      <div className="account-deletion-details">
        <p className="account-settings-header-subtitle">{ gettext('We’re sorry to see you go!') }</p>
        <p className="account-settings-header-subtitle">{ gettext('Eliminating your account and personal data is permanent and irreversible. Likewise, we will not be able to recover your account, personal data, progress, certificates, payments made among other actions carried out at Campus Romero.') }</p>
        <p className="account-settings-header-subtitle">{ gettext('Once your account is deleted, we remind you that you will no longer be able to follow our courses, specializations and any other educational offer offered through the different media, call www.campusromero.pe, Campus Romero Mobile Application (offered free of charge at the PlayStore and IOS) or in any other site managed by Campus Romero (includes access to Campus Romero from the system of your university or public/private institution). Also, you will stop immediately obtaining the benefits provided by our Campus Romero Community.') }</p>
        <p
          className="account-settings-header-subtitle"
          dangerouslySetInnerHTML={{ __html: loseAccessText }}
        />

        <Button
          id="delete-account-btn"
          className={['btn-outline-primary']}
          disabled={showError}
          label={gettext('Delete My Account')}
          inputRef={(input) => { this.modalTrigger = input; }}
          onClick={this.loadDeletionModal}
        />
        {showError &&
          <StatusAlert
            dialog={(
              <div className="modal-alert">
                <div className="icon-wrapper">
                  <Icon id="delete-confirmation-body-error-icon" className={['fa', 'fa-exclamation-circle']} />
                </div>
                <div className="alert-content">
                  {socialAuthConnected && isActive &&
                    <p dangerouslySetInnerHTML={{ __html: socialAuthError }} />
                  }
                  {!isActive && <p dangerouslySetInnerHTML={{ __html: activationError }} /> }
                </div>
              </div>
            )}
            alertType="danger"
            dismissible={false}
            open
          />
        }
        {deletionModalOpen && <StudentAccountDeletionModal onClose={this.closeDeletionModal} />}
      </div>
    );
  }
}

StudentAccountDeletion.propTypes = {
  isActive: PropTypes.bool.isRequired,
  socialAccountLinks: PropTypes.shape({
    providers: PropTypes.arrayOf(PropTypes.object),
  }).isRequired,
};
