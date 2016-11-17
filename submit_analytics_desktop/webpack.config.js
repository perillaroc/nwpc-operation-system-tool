var path = require('path');
var webpack = require('webpack');

var nodeModulesPath = path.resolve(__dirname, 'node_modules');

var entry= {
    index: './src/index.js',
    common: [
        'react',
        'react-dom',
        'react-router',
        'react-router-redux',
        'react-redux',
        'redux',
        'redux-thunk',
        'echarts',
        'jquery',
        'bootstrap'
    ]
};

var loaders= {
    loaders: [
        {
            test: /\.js$/,
            loaders: [ 'babel' ],
            exclude: /node_modules/,
            include: __dirname
        },
        {
            test: /\.less$/,
            loader: "style!css!less"
        },
        {
            test: /\.scss/,
            loader: "style!css!sass"
        },
        {
            test: path.join(nodeModulesPath, '/jquery/dist/jquery.min.js'),
            loader: 'expose?jQuery'
        },
        {
            test: /\.(woff|woff2|eot|ttf|svg)(\?.*$|$)/,
            loader: 'url-loader?importLoaders=1&limit=1000&name=/fonts/[name].[ext]'
        },
    ]
};

var resolve = {
    alias: {
        'react': path.join(nodeModulesPath, '/react/dist/react'),
        'react-dom': path.join(nodeModulesPath, '/react-dom/dist/react-dom'),
        'react-redux': path.join(nodeModulesPath, '/react-redux/dist/react-redux'),
        'react-router': path.join(nodeModulesPath, '/react-router/umd/ReactRouter'),
        'react-router-redux': path.join(nodeModulesPath, '/react-router-redux/dist/ReactRouterRedux'),
        'redux': path.join(nodeModulesPath, '/redux/dist/redux'),
        'redux-thunk': path.join(nodeModulesPath, '/redux-thunk/dist/redux-thunk'),
        'echarts': path.join(nodeModulesPath, '/echarts/dist/echarts'),
    }
};

var plugins = [
    new  webpack.optimize.CommonsChunkPlugin({
        name:"common",
        filename: "common.dist.js"
    }),
    new webpack.ProvidePlugin({
        $: "jquery",
        jQuery: "jquery"
    }),
];

var externals= {
    // 'electron': 'electron'
    // 'react': 'React',
    // 'react-dom': 'ReactDOM',
    // 'redux': 'Redux',
    // 'react-redux': 'ReactRedux',
    // 'echarts': 'echarts',
    // 'moment': 'moment',
    // 'react-router': 'ReactRouter',
    // 'react-router-redux': 'ReactRouterRedux',
    // 'redux-thunk': 'ReduxThunk'
};

module.exports = {
    devtool: "source-map",
    entry: entry,
    output: {
        path: path.join(__dirname, 'dist'),
        filename: "[name].entry.js",
        sourceMapFilename: '[file].map'
    },
    module: loaders,
    externals: externals,
    plugins: plugins,
    resolve: resolve,
    target: 'electron-renderer'
};
