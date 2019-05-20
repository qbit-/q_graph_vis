var path = require('path');
const webpack = require("webpack");
//const ExtractTextPlugin = require("extract-text-webpack-plugin");

var isDev = true

module.exports = {
	entry: path.resolve(__dirname, 'main.coffee'),
	resolve: {
		extensions: ['*', '.js', '.jsx'],
    alias: {
          'components': path.resolve('src/components'), // This is ours!!
          'src': path.resolve('src'), // This is ours!!
          'react-native': 'react-native-web'
    },
	},
	mode:'development',
    output:{
        filename: 'bundle.js',
    },
	devServer: {
		hot: true,
	},

	module: {
		rules: [
			{ test: /\.jsx?$/, exclude: /node_modules/, loaders: ['babel-loader'] },
			{ test: /\.css$/, loader: 'style-loader!css-loader' },

			{ test: /\.coffee$/, loader: 'coffee-loader', },

		]
	},
    plugins: [
        new webpack.HotModuleReplacementPlugin(),
    ],
};
