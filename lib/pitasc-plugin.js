'use babel';

import PitascPluginView from './pitasc-plugin-view';
import { CompositeDisposable } from 'atom';

export default {

  pitascPluginView: null,
  modalPanel: null,
  subscriptions: null,

  activate(state) {
    this.pitascPluginView = new PitascPluginView(state.pitascPluginViewState);
    this.modalPanel = atom.workspace.addModalPanel({
      item: this.pitascPluginView.getElement(),
      visible: false
    });

    // Events subscribed to in atom's system can be easily cleaned up with a CompositeDisposable
    this.subscriptions = new CompositeDisposable();


    // Register command that toggles this view
    this.subscriptions.add(atom.commands.add('atom-workspace', {
      'pitasc-plugin:toggle': () => this.toggle()
    }));
  },

  deactivate() {
    this.modalPanel.destroy();
    this.subscriptions.dispose();
    this.pitascPluginView.destroy();
  },

  serialize() {
    return {
      pitascPluginViewState: this.pitascPluginView.serialize()
    };
  },

  toggle() {
    console.log('PitascPlugin was toggled!');
    const { spawn } = require('child_process');
    const test = spawn('python', [__dirname + '/pitasc_boiler_plate.py -o test.dump'])
    fetch(__dirname + '/pitasc.dump')
      .then(response => response.json())
      .then(function(dd) {
        console.log(dd);
        let editor
        if (editor = atom.workspace.getActiveTextEditor()){
          editor.selectWordsContainingCursors()
          // let selection = editor.getSelectedText()
          let selection = editor.getSelections()
          console.log(selection)
          for (let s in selection) {
            console.log(selection[s])
            console.log(selection[s].getText())
            if (dd[selection[s].getText()]){
              selection[s].insertText(dd[selection[s].getText()])
            }
            else {
              // selection[s].insertText('_nope_')
            }
          }

        }
      })
  }

};
